import praw, os, time, re, json

# Setup
while True:
    try:
        client_id = os.environ["COORDBOT_CLIENT_ID"]
        client_secret = os.environ["COORDBOT_CLIENT_SECRET"]
        username = os.environ["COORDBOT_USERNAME"]
        password = os.environ["COORDBOT_PASSWORD"]

        global reddit
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
            data = {
                "subreddits": [

                ],
                "users_optout": [

                ]
            }
            with open(config_file, "w") as outfile:
                json.dump(data, outfile)
            input("Config file created! Please edit the config file to your liking, then press <ENTER> to read it!")
        else:
            with open(config_file, "r") as infile:
                try:
                    global subreddits
                    global users_optout
                    config = json.load(infile)
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


def get_link(lat, long):
    link = "https://www.google.com/maps/place/{latitude},{longitude}".format(latitude = lat, longitude = long)
    return link


# Splits a string (from post title or body) and checks for any coordinates.
def get_coords(message):
    coordinates = []
    # Scan for possible coordinates
    for index, word in enumerate(message):
        if index is len(message) - 1:
            # Since there are no more words after this one a longitude value is impossible.
            break
        try:
            testLat = re.sub("[^NESW^0-9.-]", "", word)
            testLong = re.sub("[^NESW^0-9.-]", "", message[index + 1])
        except IndexError:
            print("Error with testLat or testLong")
            break
        try:
            if testLat is "":
                raise ValueError
            elif testLat[-1] is "S":
                latitude = float(re.sub("[^0-9^.-]", "", testLat)) * -1
            else:
                latitude = float(re.sub("[^0-9^.-]", "", testLat))
            if testLong is "":
                raise ValueError
            elif testLong[-1] is "W":
                longitude = float(re.sub("[^0-9^.-]", "", testLong)) * -1
            else:
                longitude = float(re.sub("[^0-9^.-]", "", testLong))

            if not latitude >= -90 and not latitude <= 90:
                pass
            elif not longitude >= -180 and not longitude <= 180:
                pass
            else:
                # If the code has made it this far, it means we have a possible coordinate!
                coordinates.append([latitude, longitude])
                print("Coordinates found: ({lat}, {long})".format(lat=latitude, long=longitude))
        except ValueError:
            # testLat or testLong are not floats. Skip these values and test the next ones.
            pass
    if len(coordinates) > 0:
        links = ""
        for index, coordinate in enumerate(coordinates):
            link = get_link(coordinate[0], coordinate[1])
            links = links + "[Coordinate {index}]({link})\n".format(index=index + 1, link=link)
        replyText = ("I found some coordinates! Here are some links for them!  \n  \n"
                     "{links}  \n"
                     "---\n"
                     "[What is this?](https://github.com/TylrMls/CoordinateBot#coordinatebot) |"
                     " [Subreddit](https://www.reddit.com/r/CoordinateBot/)  \n"
                     "To opt out of my messages, [click here]"
                     "(https://www.reddit.com/message/compose/?to=CoordinateBot&subject=optout&message=!optout)!"
                     .format(links=links))
        return replyText
    else:
        return ""


get_subreddits()
subs = reddit.subreddit(subreddits)
# I really didn't want to do this,
# but skip_existing is required in order to deploy the bot on subreddits with lots of content
post_stream = subs.stream.submissions(pause_after=-1, skip_existing=True)
mention_stream = praw.models.util.stream_generator(reddit.inbox.mentions, pause_after=-1, skip_existing=True)
pm_stream = praw.models.util.stream_generator(reddit.inbox.messages, pause_after=-1, skip_existing=True)
while True:
    for post in post_stream:
        if post is None:
            break
        if post.author.id not in users_optout:
            print("Post ID: {id}, {title}".format(id=post, title=post.title))
            msg = post.title.split() + post.selftext.split()
            result = get_coords(msg)
            post.save()
            if result is not "":
                post.reply(result)

    for comment in mention_stream:
        if comment is None:
            break
        print("Comment ID: {id}, {message}".format(id=comment, message=comment.body))
        parent = comment.parent()
        msg = comment.body.split()
        result = get_coords(msg)
        comment.save()
        if result is not "":
            comment.reply(result)
        elif type(parent) is praw.reddit.models.Submission:
            pass
        else:
            msg = parent.body.split()
            result = get_coords(msg)
            if result is not "":
                comment.reply(result)

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
                            "(https://www.reddit.com/message/compose/?to=CoordinateBot&subject=optin&message=!optin)!")
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
