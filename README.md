# splunk-gzip-alerts
When your alert/reports sends results usually you get a plain csv email with a message like this:

 Only the first 10000 of 112552 results are included in the attached csv."

You can rise this limit but then you hit another limit at 50.000 but Splunk warns about to set it higher:

maxresultrows =
* This limit should not exceed 50000. Setting this limit higher than 50000
causes instability.

With this app the original results_file is collected, then cleans all the metadata columns and sends it in gzip format.

The compressed file is left in the app directory to check it, feel free to modify the code to do create a temp file instead.
