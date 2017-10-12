import bson
from pymongo import MongoClient


def main():
	connection = MongoClient()
	db = connection.baleen
	collection = db.posts
	col_size = collection.count()
	print("Found %d documents in baleen:posts", col_size)
	idx = 1

	col_sizes = {}
	for  post in collection.find():
		print("Item {} of {}".format(idx, col_size))
		#print(post)
		#print(post['_id'])
		#print("{} - {}".format(len(post['content']), post['_id']))
		col_sizes[post['_id']] = len(post['content'])
		idx += 1

	print(col_sizes)

	for w in sorted(col_sizes, key=col_sizes.get, reverse=True):
  		print w, col_sizes[w]


if __name__ == '__main__':
    main()
