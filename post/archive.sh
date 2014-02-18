archive_file=/data/schedules_archive/`date +"%Y-%m-%d"`_scraper.json
mongoexport --username schedules_scraper --password T49Sq8aQ5LI8y4C --db schedules --collection schedules --out $archive_file