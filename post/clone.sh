# after the schedules_temp collection has been populated, we want to clone it to the schedules collection
# clear the schedules_temp collection so its ready for tomorrow
# clear the schedules collection
# clone the schedules_temp to schedules collection
# remove the schedules_temp collection

if [ "$#" -ne 4 ]; then
    echo "You need to pass 4 params: username password host carrier"
fi

username=$1
password=$2
host=$3
carrier=$4

mongo --username $username --password $password $host/schedules --eval "db.schedules.remove({'carrier':/$carrier/i})"
mongo --username $username --password $password $host/schedules --eval "db.schedules_temp.find({'carrier':/$carrier/i}).forEach(function(x){db.schedules.insert(x);})"
mongo --username $username --password $password $host/schedules --eval "db.schedules_temp.remove({'carrier':/$carrier/i})"