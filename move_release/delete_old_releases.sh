list_releases () {
     curl -Ss https://nexus.domain.pl/nexus/service/local/repositories/<repo_id>/content/release/db/trash_working/ | grep -oP '(?<=relativePath>)[^<]+' | awk -F"/" '{print $5}'
}

list_versions () {
    curl -Ss https://nexus.domain.pl/nexus/service/local/repositories/<repo_id>/content/release/db/trash_working/${i}/ | xpath -e "/content/data/content-item/text" 2>/dev/null | awk -F'[<>]' '{print $3}'
}

porownanie_dat () {
    if [ x"$data1" '<' x"$data2" ]; then
        echo "IF:"
        echo "Data releasa ${i} wersja ${y} utworzony $data2 jest wieksza od daty ostatecznego usunięcia $data1"
    else
        echo "ELSE:"
        echo "Data releasa ${i} wersja ${y} utworzony $data2 jest mniejsza od daty ostatecznego usunięcia $data1"
        curl --request DELETE --user "deployment:<pass>" https://nexus.domain.pl/nexus/content/repositories/<repo_id>/release/db/trash_working/${i}/${y}
    fi
}

data1=`date +"%Y-%m-%d" --date="2 day ago"`

for i in `list_releases`
do
    for y in `list_versions`
    do
        data2=`curl -Ss https://nexus.domain.pl/nexus/service/local/repositories/<repo_id>/content/release/db/trash_working/${i}/${y}/ | grep -oP '(?<=lastModified>)[^<]+' | awk '{print $1}' | head -1`
        porownanie_dat
    done
    if [[ $(curl -Ss https://nexus.domain.pl/nexus/service/local/repositories/<repo_id>/content/release/db/trash_working/${i}/ | wc -w) -le 1 ]];   ##sprawdzam, czy wynikowy XML jest pusty, jezeli tak, to znaczy że nie ma wersji ani plików, czyli artefakt nie istnieje. Wywalam wtedy cały wpis o artefakcie. 
        then 
            curl --request DELETE --user "deployment:<pass>" https://nexus.domain.pl/nexus/content/repositories/<repo_id>/release/db/trash_working/${i}/ 
        else 
            echo "false"; 
    fi
done



#crontab -e 
#@daily /home/oracle/bin/delete_old_releases.sh 