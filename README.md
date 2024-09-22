To-Do's

1. Game state needs proper validations and checks 
2. Game room can be linked via foreign keys
3. Proper deployment and dockerisation. Right now I've used docker compose to link the DB and App containers, but we'll need a good architecture to launch the game clients as well, and not just the server.
4. Fix the issues in docker compose (problem while calling the postgres DB from app).

Problems:
1. Game room player ids array can have duplicate values (take care of this)
2. State and Session management is not properly implemented right now, and should be cleaned up properly (and probably use an in memory caching for sessions)
3. Although the clients and the DB itself is scalable, the central game server needs a few modifications to be stateless, and thus properly scalable (as mentioned in the above point about fixing the state and session management).
4. The client code, although independent, is somewhat dependent on naming convetions of the server. The socket management can be made better to fix this and be more resilient to minor changes in clients.
5.  

Steps To Run:

1. Make sure you have the Docker daemon installed and running, and also have docker-compose installed.
2. Go to the main directory and run `docker-compose up`.
3. Current issues are listed above, it might not work properly due to issues with container connection with postgres (fix in progress).