To-Do's

1. Game state needs proper validations and checks 
2. Game room can be linked via foreign keys
3. 

Problems:
1. Game room player ids array can have duplicate values (take care of this)
2. State and Session management is not properly implemented right now, and should be cleaned up properly (and probably use an in memory caching for sessions)
3. Although the clients and the DB itself is scalable, the central game server needs a few modifications to be stateless, and thus properly scalable (as mentioned in the above point about fixing the state and session management).
4. The client code, although independent, is somewhat dependent on naming convetions of the server. The socket management can be made better to fix this and be more resilient to minor changes in clients.
5.  