# import os
# from livekit import api
# from flask import Flask, request
# from dotenv import load_dotenv
# from flask_cors import CORS
# from livekit.api import LiveKitAPI, ListRoomsRequest
# import uuid

# load_dotenv()

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# async def generate_room_name():
#     name = "room-" + str(uuid.uuid4())[:8]
#     rooms = await get_rooms()
#     while name in rooms:
#         name = "room-" + str(uuid.uuid4())[:8]
#     return name

# async def get_rooms():
#     api = LiveKitAPI()
#     rooms = await api.room.list_rooms(ListRoomsRequest())
#     await api.aclose()
#     return [room.name for room in rooms.rooms]

# @app.route("/getToken")
# async def get_token():
#     name = request.args.get("name", "my name")
#     room = request.args.get("room", None)
    
#     if not room:
#         room = await generate_room_name()
        
#     token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
#         .with_identity(name)\
#         .with_name(name)\
#         .with_grants(api.VideoGrants(
#             room_join=True,
#             room=room
#         ))
    
#     return token.to_jwt()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)






# # from flask import Flask, request
# # from flask_cors import CORS
# # from livekit import api
# # import os

# # app = Flask(__name__)
# # CORS(app)

# # @app.route("/")
# # def home():
# #     return "Backend running!"

# # @app.route("/getToken")
# # def get_token():
# #     try:
# #         name = request.args.get("name", "guest")
# #         room = request.args.get("room", "default-room")

# #         token = api.AccessToken(
# #             os.environ.get("LIVEKIT_API_KEY"),
# #             os.environ.get("LIVEKIT_API_SECRET"),
# #         )

# #         token.identity = name

# #         # ✅ FIX HERE
# #         token.add_grant(
# #             api.Grant(
# #                 room_join=True,
# #                 room=room
# #             )
# #         )

# #         return token.to_jwt()

# #     except Exception as e:
# #         print("❌ ERROR:", str(e))
# #         return {"error": str(e)}, 500


# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5001, debug=True)





import os
import uuid
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api

# Load your .env file
load_dotenv(".env.local") # Change this if your .env file has a different name

app = Flask(__name__)
CORS(app) # Allows the frontend to talk to this server

@app.route("/getToken")
def get_token():
    try:
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            print("❌ ERROR: Missing API Key or Secret in .env")
            return "Server Configuration Error", 500

        # Get identity from frontend, or create a random guest name
        name = request.args.get("name", "guest-" + str(uuid.uuid4())[:4])
        room = request.args.get("room", "test-room")
        
        print(f"Generating token for: {name} in room: {room}")

        # Create the access token
        token = api.AccessToken(api_key, api_secret) \
            .with_identity(name) \
            .with_name(name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room
            ))
        
        return token.to_jwt()

    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    # We use port 5001 to match your Vite Proxy
    app.run(host="0.0.0.0", port=5001, debug=True)