# Motion SDK Python Example

Stream measurement and motion data from the Shadow. Print out the data in
CSV format.

Each sample in time is one row. Each column is one channel from one device
or joint in the Shadow skeleton.

## Run the example

By default, the example application will read as many samples as possible and
print them to the standard output. The samples are printed as they arrive,
every ~10 milliseconds.

```
python example.py  --help

usage: example.py [-h] [--file FILE] [--frames FRAMES] [--header]
                  [--host HOST] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --file FILE      output file
  --frames FRAMES  read N frames
  --header         show channel names in the first row
  --host HOST      IP address of the Motion Service
  --port PORT      port number of the Motion Service
```
