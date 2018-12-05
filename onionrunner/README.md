# First Tool

## Installation

First of all run `apt-get update`. Then install dependencies by doing: `apt-get install tor git bison libexif-dev`, and `apt-get install python-pip`.

Run `pip install stem` and finally install the Go language.

Once all this is done go ahead ant install onionscanner using `go get github.com/s-rah/onionscan` and `go install github.com/s-rah/onionscan`. To check that the installation went good, just type `onionscan` in your terminal, and you should see the command line usage information.

Now we need to modify the Tor configuration, this in order to allow our software to get a new identity if we get stuck during the scans.

Do this by running `tor --hash-password YourPassword`. You will get a string like this: `16:9835E27256682AB56990E38751C5713CC26E711187EA0AED357C4C4161`, copy it.

Then, go in `/etc/tor/torrc` and add these three lines at the bottom of the file:
```
ControlPort 9051
ControlListenAddress 127.0.0.1
HashedControlPassword 16:3E73307B3E434914604C25C498FBE5F9B3A3AE2FB97DAF70616591AAF8
```
Please remember to put your own password hash there!

Finally, run `service tor restart`

