import re

#test your phone number validator. zero or more reps

re1=r'#[\w]+[a-zA-Z]+'
tweets="kjawh #wldj lakwj #k1wjd","kjawh #wrldj lakwj #k1wjd","kjawh #wldgj lakwj #kw2jd","kjawh #wldj lakwj #kwjd"

hashtag="#wldj"
for a,tweet in enumerate(tweets):
  for x in re.findall(re1,tweet):
    if x==hashtag:
      print('found ', a )