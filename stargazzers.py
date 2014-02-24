'''
Tool for downloading additional data into a dataset of most popular repositories
(aggregated data maximum(sum(delta_stargazing)) from Google BigQuery)
Nickname: Dubnadium
@version 1.1
@since 1.0
@author Oskar Jarczyk
'''

import csv
import codecs
import cStringIO
from github import Github, UnknownObjectException
import time
import scream
import gc
import __builtin__


quota_check = 0
auth_with_tokens = True
filename__ = 'result_stargazers_2013_final_mature.csv'
__builtin__.verbose = True


class MyDialect(csv.Dialect):
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_MINIMAL
    delimiter = ';'
    escapechar = '\\'
    quotechar = '"'
    lineterminator = '\n'


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=MyDialect, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=MyDialect, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def check_quota_limit():
    global quota_check
    quota_check += 1
    if quota_check > 9:
        quota_check = 0
        limit = gh.get_rate_limit()
        scream.say('Rate limit: ' + str(limit.rate.limit) +
                   ' remaining: ' + str(limit.rate.remaining))
        reset_time = gh.rate_limiting_resettime
        scream.say('Rate limit reset time: ' + str(reset_time))

        if limit.rate.remaining < 10:
            freeze()


def freeze():
    sleepy_head_time = 60 * 60
    time.sleep(sleepy_head_time)
    limit = gh.get_rate_limit()
    while limit.rate.remaining < 15:
        time.sleep(sleepy_head_time)


def freeze_more():
    freeze()


LIMIT_DATA = False
LIMIT_COUNT = 2000


if __name__ == "__main__":
    scream.say('Start main execution')
    scream.say('Welcome to WikiTeams.pl small dataset enricher!')

    secrets = []
    credential_list = []
    with open('pass.txt', 'r') as passfile:
        line__id = 0
        for line in passfile:
            line__id += 1
            secrets.append(line)
            if line__id % 4 == 0:
                login_or_token__ = str(secrets[0]).strip()
                pass_string = str(secrets[1]).strip()
                client_id__ = str(secrets[2]).strip()
                client_secret__ = str(secrets[3]).strip()
                credential_list.append(
                    {'login': login_or_token__, 'pass': pass_string,
                     'client_id': client_id__,
                     'client_secret': client_secret__}
                )
                del secrets[:]

    scream.say(str(len(credential_list)) +
               ' full credentials successfully loaded')

    if auth_with_tokens:
        gh = Github(client_id=credential_list[0]['client_id'],
                    client_secret=credential_list[0]['client_secret'])
        print credential_list[0]['client_id']
        print credential_list[0]['client_secret']
        print gh.oauth_scopes
        print gh.rate_limiting
    else:
        #print login_or_token__
        #print pass_string
        gh = Github(credential_list[0]['login'], credential_list[0]['pass'])

    is_gc_turned_on = 'turned on' if str(gc.isenabled()) else 'turned off'
    scream.say('Garbage collector is ' + is_gc_turned_on)

    i = 0

    with open(filename__, 'rb') as source_csvfile:
        reposReader = UnicodeReader(source_csvfile)
        with open('result_stargazers_2013_final_mature_stargazers.csv', 'ab') as stargazers_csvfile:
            stargazers_writer = UnicodeWriter(stargazers_csvfile)
            with open('result_stargazers_2013_final_mature_contributors.csv', 'ab') as contributors_csvfile:
                contributors_writer = UnicodeWriter(contributors_csvfile)
                with open('result_stargazers_2013_final_mature_stars.csv', 'ab') as output_csvfile:
                    moredata_writer = UnicodeWriter(output_csvfile)
                    reposReader.next()
                    with open('result_stargazers_2013_final_mature_err.csv', 'ab') as err_csvfile:
                        errdata_writer = UnicodeWriter(output_csvfile)
                        for row in reposReader:
                            try:
                                i = i + 1
                                owner = row[0]
                                url = row[1]
                                scream.say('url: ' + url)
                                name = row[2]
                                key = str(owner + '/' + name)
                                scream.say(key)
                                repository = gh.get_repo(key)
                                stargazers_count = repository.stargazers_count
                                row.append(str(stargazers_count))
                                scream.say('stargazers: ' + str(stargazers_count))
                                contributors_list = repository.get_contributors()
                                stargazers_list = repository.get_stargazers()
                                how_many_contributors = 0
                                how_many_stargazers = 0
                                for contributor in contributors_list:
                                    how_many_contributors += 1
                                    contributors_writer.writerow([url, contributor.login])
                                for stargazer in stargazers_list:
                                    how_many_stargazers += 1
                                    stargazers_writer.writerow([url, stargazer.login])
                                scream.say('contributors: ' + str(how_many_contributors))
                                row.append(str(how_many_contributors))
                                scream.say('stargazers: ' + str(how_many_stargazers))
                                row.append(str(how_many_stargazers))
                                moredata_writer.writerow(row)
                                if LIMIT_DATA and (i > LIMIT_COUNT):
                                    break
                                check_quota_limit()
                            except TypeError:
                                errdata_writer.writerow(row)
                            except UnknownObjectException:
                                errdata_writer.writerow(row)
                    output_csvfile.close()
                    err_csvfile.close()
                contributors_writer.close()
            stargazers_writer.close()
