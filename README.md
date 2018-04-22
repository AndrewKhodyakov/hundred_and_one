Test task repository consist of two parts:

    1. Data loader
        * get from environ: 
            SOURSE_URL - url for data loading (requred), 
            FROM_DATE - first date limit (requred), 
            TO_DATE - last date limit (only one is requred),
            DB_URL - path to database (only one is requred)
            RETRY_TIMEOUT - retry timeout bettwen load data attempts (default=600 seconds)
            TMP_FOLDER - folder for temporary files
            DEBUG - more verbose regimen

        *create connection, to database (?create models by exists schema?)
            
        * detect reqired date duration:
            if limits not exists - riase ValueError;
            if only one limit exists - get data only for one date
            if exists couple limits - generate data ranges for requests

        * make requests by url (if not req.ok - retry)
        * decompress data (date limit define archive format zip before 20081201, and rar since 2009)
        * create models instances and save it in database (encoding=cp866) 

    2. REST-service for looking for data by organizations through its REGN
            DB_URL - path to database

            DB_SCHEMA:
                hundred_and_one - (*B1.DBF)
                    REGN - ForeginKey to Organization table
                    year_month - data for the period
                    fields according to 101 format description          
