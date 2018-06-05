#!/usr/bin/env python

import smtplib
import gzip
import csv
import tempfile
import sys
import StringIO
import json
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys, os, datetime
import json

def log(msg):
    f = open(os.path.join(os.environ["SPLUNK_HOME"], "var", "log", "splunk", "mailgz.log"), "a")
    print >> f, str(datetime.datetime.now().isoformat()), msg
    f.close()

def remove_fields(results_in):
    # Remove fields beginning with _
    with gzip.open(results_in) as infile, gzip.open('out.csv', 'wb') as outfile:
        reader = csv.reader(infile)
        i = reader.next()
        fields = filter(lambda x: not x.startswith('_'), i)
        print fields
        infile.seek(0)
        r = csv.DictReader(infile)
        w = csv.DictWriter(outfile, fields, extrasaction="ignore")
        w.writeheader()
        for row in r:
            w.writerow(row)
    return outfile.name

def send_file(the_file, settings):
    try:
        config = settings['configuration']
        recipients = config['recipients']
        results_link = settings['results_link']
        search_name = settings['search_name']
        sender = 'splunk@mydomain.com'
        log("Sending alert %s to: %s" %(search_name,recipients))
        # Create the message
        themsg = MIMEMultipart()
        themsg['Subject'] = 'Splunk results for %s' % search_name
        #themsg['To'] = ','.join(recipients)
        themsg['To'] = recipients
        themsg['From'] = sender
        themsg.preamble = 'I am not using a MIME-aware mail reader.\n'
        text = "Your search has returned %s events.\nView custom alert results in Splunk: %s" %(config['result_count'],results_link)
        part1 = MIMEText(text, 'plain')
        part2 = MIMEBase('application', 'gzip')
        part2.set_payload(open(the_file, "rb").read())
        encoders.encode_base64(part2)
        part2.add_header('Content-Disposition', 'attachment', filename=search_name + '.csv.gz')
        themsg.attach(part1)
        themsg.attach(part2)
        themsg = themsg.as_string()

        # send the message
        smtp = smtplib.SMTP()
        smtp.connect()
        smtp.sendmail(sender, recipients, themsg)
        smtp.close()
    except Exception, e:
        print >> sys.stderr, "Error Error %s" % e
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "--execute":
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)
    else:
        settings = json.loads(sys.stdin.read())
        send_file(remove_fields(settings['results_file']),settings)


