from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    # @staticmethod
    # def read_status_actuatoren():
    #     sql = "SELECT * from Actuator"
    #     return Database.get_rows(sql)

    @staticmethod
    def read_sensors():
        sql = "SELECT * from Sensor"
        return Database.get_rows(sql)

    @staticmethod
    def get_acuatoren():
        sql = "SELECT * from Acuator"
        return Database.get_rows(sql)

    @staticmethod
    def read_latest_measurements():
        sql = "SELECT s.naam, his.waarde, s.meeteenheid,s.beschrijving,s.codeSens, IF(timestamp >= DATE_SUB(NOW(), INTERVAL 30 MINUTE), 1, 0) as `recent` FROM Historiek his INNER JOIN(SELECT sensor, MAX(timestamp) as MAXTIME FROM Historiek GROUP BY sensor) h join Sensor s ON s.codeSens = his.sensor and his.sensor = h.sensor and his.timestamp = h.MAXTIME  "
        return Database.get_rows(sql)

    @staticmethod
    def read_latest_score():
        sql = 'SELECT score,IF(timestamp >= DATE_SUB(NOW(), INTERVAL 30 MINUTE), 1, 0) as `recent` FROM smartAir.Score group by timestamp DESC LIMIT 1;'
        return Database.get_one_row(sql)

    @staticmethod
    def read_status_actuatoren():
        sql = "SELECT a.naam, his.waarde, IF(timestamp >= DATE_SUB(NOW(), INTERVAL 30 MINUTE), 1, 0) as `recent` FROM Historiek his INNER JOIN(SELECT acuator, MAX(timestamp) as MAXTIME FROM Historiek GROUP BY acuator) h join Acuator a ON a.codeAcua = his.acuator and his.acuator = h.acuator and his.timestamp = h.MAXTIME  "
        return Database.get_rows(sql)

    @staticmethod
    def add_measurement(waarde, time, sensor, acuator):
        sql = "INSERT INTO Historiek (waarde,timestamp,sensor,acuator) VALUES (%s,%s,%s,%s)"
        params = [waarde, time, sensor, acuator]
        return Database.execute_sql(sql, params)

    @staticmethod
    def add_score(score, tijd):
        sql = "INSERT INTO Score (Score,Timestamp) VALUES (%s,%s)"
        params = [score, tijd]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_all_measurements(sensor):
        sql = "SELECT * from Historiek h join Sensor s on s.codeSens=h.sensor where h.sensor=%s"
        params = [sensor]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_all_measurements_by_time(tijd, sensor):
        sql = f"SELECT * from Historiek h join Sensor s on s.codeSens = h.sensor where timestamp BETWEEN NOW()-interval 1 {tijd} AND NOW() and h.sensor=%s"
        params = [sensor]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_all_measurements_by_datepicker(tijd, sensor):
        sql = f"SELECT * from Historiek h join Sensor s on s.codeSens = h.sensor where CAST(h.timestamp As date)=%s and h.sensor=%s"
        params = [tijd, sensor]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_all_measurements_by_weekpicker(tijd, sensor):
        sql = f"SELECT * from Historiek h join Sensor s on s.codeSens = h.sensor where week(h.timestamp,1)=%s and h.sensor=%s"
        params = [tijd, sensor]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_tips():
        sql = "SELECT * FROM Tips"
        return Database.get_rows(sql)
