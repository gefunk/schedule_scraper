# after the schedules_temp collection has been populated, we want to clone it to the schedules collection
# clear the schedules_temp collection so its ready for tomorrow
# clear the schedules collection
# clone the schedules_temp to schedules collection
# remove the schedules_temp collection

mongo_commands[0]="db.schedules.remove()"
mongo_commands[1]="db.schedules_temp.find().forEach(function(x){db.schedules.insert(x);})"
mongo_commands[2]="db.schedules_temp.remove()"

echo $mongo_commands

for command in ${mongo_commands[*]}
do
    echo "Running: $command"
    mongo localhost/schedules --eval $command
done

