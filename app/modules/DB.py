import csv
import pymysql
import glob

class Database(object):
    # Class for handlign mysql database for schedule storage

    def __init__(self, host, password, user):
        self.db = pymysql.connect(host,
            'user',
            'password',
            'db',
            cursorclass=pymysql.cursors.DictCursor)
        # Set at default credentials in docker-compose
    
    def update(self):
        # Upload schedule data to db

        print("Updating schedule...")
        cursor = self.db.cursor()
        sqlDropIfExists = "DROP TABLE IF EXISTS Schedule"
        cursor.execute(sqlDropIfExists)
        sqlCreateTableCommand = "CREATE TABLE Schedule(Month VARCHAR(16), Day VARCHAR(2), Name VARCHAR(32), Start VARCHAR(8), End VARCHAR(8))"
        cursor.execute(sqlCreateTableCommand)

        # Check only CSV files and iterate
        for schedule in glob.glob('assets/schedules/*.csv'):
            csv_data = csv.reader(open(schedule))
            next(csv_data)
            for row in csv_data:
                cursor.execute('INSERT INTO Schedule (Month, Day, Name, Start, End) VALUES(%s, %s, %s, %s, %s)',row)

        self.db.commit()
        cursor.close()
        print("Done Updating Schedule!")

    def retrieveSchedule(self, calendar):
        # Add db data to caledar object, dictionary with tuple keys (month, date)
        print("Retrieving schedule...")
        cursor = self.db.cursor()

        cursor.execute("SELECT * FROM Schedule")
        rows = cursor.fetchall()
        for line in rows:
            month = line["Month"]
            day = line["Day"]
            msg = line["Name"]
            start = line["Start"]
            end = line["End"]
            #Format hr:min to decimal
            start = start.split(":")
            hr = int(start[0])
            min = int(start[1]) / 60
            startFormatted = hr + min
            end = end.split(":")
            hr = int(end[0])
            min = int(end[1]) / 60
            endFormatted = hr + min
            temp = [("event", "none", startFormatted, endFormatted, msg)]
            if ((month,day) not in calendar):
                calendar[(month,day)] = temp
            else:
                calendar[(month,day)] += temp

        self.db.commit()
        cursor.close()
        print("Done Retrieving Schedule!")
        return calendar