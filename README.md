# CoordinateBot
A bot that finds possible coordinates in a message or post title and creates a clickable link!

## How it works
The bot uses the [Python Reddit API Wrapper (PRAW)](https://praw.readthedocs.io/en/latest/) to get posts in specific subreddits. It then splits the post title (and post body if applicable) and removes any non-numeric characters, after which it checks for any possible coordinates and upon finding a pair of coordinates creates a Google Maps link.

## How to use
### Posts
Good news! For posts, coordinates are automatically found and posted in the comments for various subreddits!

However, if the bot does not automatically post a link and you would like it to, you can simply tag it in a comment. The bot checks whatever post you commented on, so if you would like a link for coordinates in a post's title or body, make sure you comment on the post itself, as replying to any comments will only return a link if the comment you've replied to contains possible coordinates.

### Comments
As stated above, tag the bot in a reply to a comment to get a link for any coordinates found.

~~I also plan on adding the ability to provide your own coordinates in your call to the bot, however this is not implemented in v1.0.~~
This feature has been added! Just include your coordinates in your comment to get the links!

## Contact Me
You can contact me by sending me a PM ([u/TheTowerBay](https://www.reddit.com/user/TheTowerBay)) or though GitHub (however, please note that I am not as active here).

If you have any bugs to report, features to request, or any other comments regarding the bot, use the contact info above or join me in [r/CoordinateBot](https://www.reddit.com/r/CoordinateBot/)!
