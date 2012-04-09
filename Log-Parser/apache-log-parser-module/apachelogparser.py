#!/usr/bin/python
#       apachelogparser.py
#
#       Copyright 2010 Vasudev Kamath <kamathvasudev@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

__version__ = "1.0"
__author__ = "Vasudev Kamath <kamathvasudev@gmail.com>"
__license__ = "GPL v3.0"

import os
import sys


class ApacheLogParser:
    def __init__(self):
        # "Access" for access log
        # "Error" for error log
        self.log_type = None
    
    def __check_format__(self, line):
        '''
           This function is used to check if a given line of access log
           is in "common" format or "combined" format
           @param line Line to be checked
           @return format string ("Combined" "Common")
        '''
        # If the index 10 and higher exist then the log format is
        # "combined" else its "common"
        format = "Combined"

        try:
            # Index 10 of list is referer if this exist then
            # format is Combined else its common
            i = line[10]
        except IndexError:
            format = "Common"

        return format

    def __list_to_string__(self, list_line):
        '''
           This function converts a given list into space seperated
           string. If log being parsed is access log then this
           removes "" or [] in the begining and end of the string else
           string is returned as its it

           @param list_line List type data representing a field
           @return string form of the given list
        '''
           
        return_str = str()
        for i in list_line:
            return_str += " " + i

        # if log is access log remove the quotes or [] before returning
        if self.log_type == "Access":
            return return_str[2:-1]
        elif self.log_type == "Error":
            return return_str
     

class ApacheAccessLogParser(ApacheLogParser):
    '''
       This class represents single line in access log
       either in combined or common format. This is derived
       from ApacheLogParser class
    '''
    def __init__(self):
        self.log_type = "Access"
        self.ip_address = None

        # RFC 1431 client identity determined by the identd on client machine
        # if this filed is "-" then no identity information is avaliable
        self.client_identity = None

        # User ID of the user requesting document via HTTP authentication. If
        # the document is not protected then this filed will be "-"
        self.user_id = None

        # Time of the request
        self.date = None

        # Request information Eg "GET /favicon.ico HTTP 1.0"
        self.request = None

        # This is response number sent for the request 200 for OK
        self.response = None

        # Size of response sent this will be "-" if nothing is returned or 0
        # if %B is used
        self.response_size = None

        # These fields will be present only if combined log format is used
        self.referer = None 
        self.user_agent = None

    def parse(self, line):
        '''
           This function parses the given line of access log and extracts all
           fields. Function assumes access log line format is default as
           specified in this Apache documentation

           http://httpd.apache.org/docs/2.1/logs.html

           @param line Log line to be parsed
           @return nothing fields of object are filled with values from line

           Note that this function assumes following format for log line

           localhost - -
           [31/May/2010:10:41:17 +0530]
           "GET /favicon.ico HTTP/1.1"
           404 510 "-"
           "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.9) Gecko/20100501
           Iceweasel/3.5.9 (like Firefox/3.5.9)"

           and is not intelligent enough to validate line passed to it to make
           sure its from acces log itself. Developers using this module should
           take care of this else module may give you junk output ;)

        '''
        
        # First get common fields of the log

        # Split the log line on spaces
        log_line = line.split()

        # The first field in the list will be ip address
        self.ip_address = str(log_line[0])

        # Next field will be identity of client as per RFC 1431
        # given by identd daemon
        self.client_identity = str(log_line[1])

        # User ID if requested resource is protected by Apache's
        # directory / folder protection
        self.user_id = str(log_line[2])

        # Fields from 3-5 is date and time of request with time zone
        self.date = self.__list_to_string__(log_line[3:5])

        # Fields from 5-8 forms the request information
        self.request = self.__list_to_string__(log_line[5:8])

        # Field 8 forms the response number sent by Apache
        self.response = str(log_line[8])

        # Field 9 is size of response sent
        self.response_size = str(log_line[9])

        # Now its time to check if the line is in Common or Combined format
        # If in the combined format get referer and the User-agent 
        if self.__check_format__(log_line) == "Combined":
            self.referer = str(log_line[10])
            self.user_agent = self.__list_to_string__(log_line[11:])        


class ApacheErrorLogParser(ApacheLogParser):
    '''
       This class extracts as much information as possible from
       error log line. Since there is no proper format for error
       log line this may go wrong also. :)
    '''
    
    def __init__(self):
        self.log_type = "Error"
        self.date = None
        self.type = None
        self.description = None
        self.cleint_ip = None

    def parse(self, line):
        '''
           This function parses the error log line and assumes the log
           line format as mentioned in this link

           http://httpd.apache.org/docs/2.1/logs.html

           [Sat May 29 16:57:34 2010]
           [error]
           [client 127.0.0.1]
           File does not exist: /var/www/favicon.ico

           Note that this function is not intelligent enough to validate
           the line to check its a valid error log line or not. So its up
           to end user to provide valid error log line
        '''
        
        log_line = line.split()

        # Field from 0-5 represents date time remove the
        # [] of resulting string.
        self.date = self.__list_to_string__(log_line[0:5])[2:-1]

        # Whether this line is info error debug warn etc
        self.type = str(log_line[5])

        # Final chunk from field 6- end represents error description.
        self.description = self.__list_to_string__(log_line[6:])

        # If the description contains string client then extract the ip and
        # adjust the description to exlude [client 127.0.0.1] part
        if self.description.find("client"):
            self.client_ip = log_line[7][:-1]
            self.description = self.__list_to_string__(log_line[8:])
