import os
import praw
import prawcore
import time
import json
import coordhandler

# setup
while True:
    try:
        client_id = os.environ["COORDBOT_CLIENT_ID"]
        client_secret = os.environ["COORDBOT_CLIENT_SECRET"]
        username = os.environ["COORDBOT_USERNAME"]
        password = os.environ["COORDBOT_PASSWORD"]

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent="Coordinate Bot v1.0 (by u/TheTowerBay)"
        )
        break
    except KeyError:
        print("Login failed! Trying again in 10 seconds...")
        time.sleep(10)

config_file = "config.json"
subreddits = ""
users_optout = []


# Used to generate the list of subreddits to watch.
def get_subreddits():
    while True:
        if not os.path.isfile(config_file):
            config_data = {
                "subreddits": [

                ],
                "users_optout": [

                ]
            }
            with open(config_file, "w") as config_outfile:
                json.dump(config_data, config_outfile)
            input("Config file created! Please edit the config file to your liking, then press <ENTER> to read it!")
        else:
            with open(config_file, "r") as config_infile:
                try:
                    global subreddits
                    global users_optout
                    config = json.load(config_infile)
                    if len(config["subreddits"]) == 0:
                        print("No subreddits to monitor! Retrying in 5 seconds...")
                        time.sleep(5)
                    subreddits = '+'.join(config["subreddits"])
                    print(subreddits)
                    users_optout = config["users_optout"]
                    break
                except KeyError:
                    print("Error reading config file! Retrying in 5 seconds...")
                    time.sleep(5)


def get_response(coordinate_list):
    links = ""
    for coordinate_index, coordinate in enumerate(coordinate_list):
        link = get_link(coordinate[0], coordinate[1])
        links = links + "[Coordinate {index}]({link})  \n".format(index=coordinate_index + 1, link=link)
    return ("I found some potential coordinates! Here are some links for them!  \n  \n"
            "{links}  \n"
            "---\n"
            "[What is this?](https://github.com/TylrMls/CoordinateBot#coordinatebot) |"
            " [Subreddit](https://www.reddit.com/r/CoordinateBot/)  \n"
            "To opt out of my messages, [click here]"
            "(https://www.reddit.com/message/compose/"
            "?to=CoordinateBot&subject=optout&message=!optout)!"
            .format(links=links))


def get_link(lat, long):
    link = "https://www.google.com/maps/place/{latitude},{longitude}".format(latitude=lat, longitude=long)
    return link


get_subreddits()
subs = reddit.subreddit(subreddits)

post_stream = subs.stream.submissions(pause_after=-1, skip_existing=True)
mention_stream = praw.models.util.stream_generator(reddit.inbox.mentions, pause_after=-1, skip_existing=True)
pm_stream = praw.models.util.stream_generator(reddit.inbox.messages, pause_after=-1, skip_existing=True)
while True:
    try:
        for post in post_stream:
            if post is None:
                break
            if post.author.id not in users_optout:
                print("Post ID: {id}, {title}".format(id=post, title=post.title))
                msg = post.title.split() + ["/"] + post.selftext.split()
                coordinates = coordhandler.get_coordinates(msg)
                post.save()
                if len(coordinates) != 0:
                    post.reply(get_response(coordinates))

        for comment in mention_stream:
            if comment is None:
                break
            print("Comment ID: {id}, {message}".format(id=comment, message=comment.body))
            parent = comment.parent()
            msg = comment.body.split()
            coordinates = coordhandler.get_coordinates(msg)
            comment.save()
            if len(coordinates) != 0:
                comment.reply(get_response(coordinates))
            elif type(parent) is praw.reddit.models.Submission and parent is not None:
                print("Parent ID: {id}, {title}".format(id=parent, title=parent.title))
                msg = parent.title.split() + ["/"] + parent.selftext.split()
                coordinates = coordhandler.get_coordinates(msg)
                comment.save()
                if len(coordinates) != 0:
                    comment.reply(get_response(coordinates))
            elif type(parent) is praw.reddit.models.Comment and parent is not None:
                print("Parent ID: {id}, {body}".format(id=parent, body=parent.body))
                msg = parent.body.split()
                coordinates = coordhandler.get_coordinates(msg)
                comment.save()
                if len(coordinates) != 0:
                    comment.reply(get_response(coordinates))

        for pm in pm_stream:
            if pm is None:
                break
            if pm.subject == "optout" and pm.body == "!optout":
                with open(config_file, "r") as infile:
                    data = json.load(infile)
                    if pm.author.id in data["users_optout"]:
                        print("User {user} attempted to opt out but is already on the list!".format(user=pm.author.id))
                    else:
                        with open(config_file, "w") as outfile:
                            data["users_optout"].append(pm.author.id)
                            users_optout.append(pm.author.id)
                            json.dump(data, outfile)
                            pm.reply("Successfully opted out! To opt back in, [click here]"
                                     "(https://www.reddit.com"
                                     "/message/compose/?to=CoordinateBot&subject=optin&message=!optin)!")
            if pm.subject == "optin" and pm.body == "!optin":
                with open(config_file, "r") as infile:
                    data = json.load(infile)
                    if pm.author.id not in data["users_optout"]:
                        print("User {user} attempted to opt in but is not on the list!".format(user=pm.author))
                    else:
                        for index, user in enumerate(data["users_optout"]):
                            if pm.author.id == user:
                                with open(config_file, "w") as outfile:
                                    users_optout.pop(index)
                                    data["users_optout"].pop(index)
                                    json.dump(data, outfile)
                        pm.reply("Successfully opted in! To opt back out, [click here]"
                                 "(https://www.reddit.com"
                                 "/message/compose/?to=CoordinateBot&subject=optout&message=!optout)!")
    except (prawcore.exceptions.ServerError, prawcore.exceptions.RequestException) as e:
        print("Error occurred while making a request to Reddit server.")
        print(e)
        print("Resuming requests in 10 seconds...")
        time.sleep(10)
	continue

