import dataset
def one():
    db = dataset.connect('sqlite:///test.db')

    table = db['sometable']
    table.insert(dict(name='John Doe', age=37))
    table.insert(dict(name='Jane Doe', age=34, gender='female'))
    db.commit()
def read():
    db = dataset.connect('sqlite:///test.db')
    table = db['sometable']
    john = table.find_one(name='John Doe')
    print(john['age'])
read()