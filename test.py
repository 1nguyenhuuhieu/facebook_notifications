str = "https://www.facebook.com/groups/2436942816413232/?multi_permalinks=5720368821403932%2C5720364364737711%2C5720349264739221%2C5720343794739768%2C5720337841407030&notif_id=1669863541166489&notif_t=group_activity&ref=notif"

list_str = str.split("/")

post = list_str[5]

list_post = post.split("=")

post_id = list_post[1].split("%")
post_id = post_id[0].split("&")
print(post_id[0])