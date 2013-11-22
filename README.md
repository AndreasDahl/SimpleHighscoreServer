SimpleHighscoreServer
=====================

Protocol
--------

### Server Responses

#### Initial responses:
`100 CONNECTED`
`101 TAKEN`
`102 HANDSHAKE EXPECTED`
    
#### Post responses:
`200 POST SUCCESS`
`201 POST REJECTED`
`202 TIME INVALID`

#### Lookup responses
`300 INFO <number_of_entries> <name> <time> <name> <time> ...`
`301 BAD REQUEST`

#### Leave responses:
`400 BYE`
  
#### Generic Responses:
`500 BAD FORMAT`
  
### Supported Requests:
`HELLO`

`POST <name> <time>`
example : POST Andreas 72000000000
post a time of 1:12.0000 under the name Andreas

`TOP <n>`
Request n lookup responses for the n highest scores on the server

`LEAVE`
Notify the server, that you are leaving.i

Protocol Usage
--------------

TODO
