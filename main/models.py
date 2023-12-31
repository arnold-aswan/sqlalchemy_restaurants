

from sqlalchemy import and_,create_engine, ForeignKey, Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

restaurant_customers = Table(
    'restaurant_customers',
    Base.metadata,
    Column('restaurant_id', ForeignKey('restaurants.id'), primary_key=True),
    Column('customer_id', ForeignKey('customers.id'), primary_key=True),
    extend_existing=True,
)

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    price = Column(Integer())
    
    review = relationship('Review', backref='restaurants')
    customers = relationship('Customer', secondary='restaurant_customers', back_populates='restaurants')
    
    def __init__(self, name, price):
        self.id = None
        self.name = name
        self.price = price
        
    def __repr__(self):
        return f'(Restaurant = {self.name}, ' + \
            f'price= {self.price})'   
    
    def reviews(self):
        # returns a collection of all the reviews of the restaurant instance
        reviews = session.query(Review).filter(Review.restaurant_id == self.id).all()
        # return [review.rating for review in reviews]
        return reviews
    
    def restaurant_customers(self):
        # returns a collection of all the customers who reviewed the `Restaurant`
        customers = session.query(Customer).join(Review).filter(Review.restaurant_id == self.id).all()
        return [customer.first_name for customer in customers]
    
    def all_reviews(self):
        # return an list of strings with all the reviews for this restaurant
        reviews = session.query(Review).join(Restaurant).join(Customer).\
            filter(Review.restaurant_id == self.id).all()   
        
        reviewed= [review.full_review() for review in reviews]
        return reviewed
    
    @classmethod
    def fanciest(cls):
        # returns _one_ restaurant instance for the restaurant that has the highest   price
        restaurant = session.query(Restaurant).order_by(Restaurant.price.desc()).first()
        print(restaurant)
          
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer(), primary_key=True)
    first_name = Column(String())
    last_name = Column(String())    
    
    review = relationship('Review', backref='customers')
    restaurants = relationship('Restaurant', secondary='restaurant_customers', back_populates='customers')
    
    def __init__(self, first_name, last_name):
        self.id = None
        self.first_name = first_name
        self.last_name = last_name
        
    def __repr__(self):
        return f'(firstName = {self.first_name}, ' + \
            f'lastName = {self.last_name})'    
            
    def reviews(self):
        #  should return a collection of all the reviews that the `Customer` has left
        reviews = session.query(Review).filter(self.id == Review.customer_id).all()
        return [review.rating for review in reviews]
            
    def customer_restaurants(self):
        # returns the restaurant instance that has the highest star rating from this customer
        restaurants = session.query(Restaurant).join(Review).filter(Review.customer_id == self.id).all()
        return [restaurant.name for restaurant in restaurants]
    
    def full_name(self):
        # returns the full name of the customer, with the first name and the last name  concatenated, Western style.
        return f"{self.first_name} {self.last_name}"
    
    def favorite_restaurant(self):
        #  returns the restaurant instance that has the highest star rating from this customer
        favorite = session.query(Restaurant).\
            join(restaurant_customers).\
            join(Review, Restaurant.id == Review.restaurant_id).\
                filter(restaurant_customers.c.customer_id == self.id).\
                    order_by(Review.rating.desc()).\
                        first()
        return favorite                
        
    def add_review(self, rating, restaurant_id):   
        # creates a new review for the restaurant with the given `restaurant_id`
        review = Review(rating = rating, restaurant_id = restaurant_id, customer_id = self.id)  
        session.add(review)
        session.commit()
        print('review added')
        
    def delete_reviews (self, restaurant):
        # removes **all** their reviews for this restaurant
        reviews = session.query(Review).\
            filter(and_(Review.customer_id == self.id, Review.restaurant_id == restaurant.id)).all()
        print(reviews)    
    
        for review in reviews:
            session.delete(review)
        
            
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer(), primary_key=True)
    rating = Column(Integer())
    restaurant_id = Column(Integer(), ForeignKey('restaurants.id'))
    customer_id = Column(Integer(), ForeignKey('customers.id'))
    
    
    def __init__(self, rating, restaurant_id, customer_id):
        self.rating = rating
        self.restaurant_id = restaurant_id
        self.customer_id = customer_id
    
    def __repr__(self):
        return f'(rating = {self.rating}, ' + \
            f'restaurant_id = {self.restaurant_id}, ' + \
            f'customer_id = {self.customer_id})'
            
    def customer(self):
        # Returns the customer instance for this review
        customer = session.query(Customer).join(Review).filter(Review.id == self.id).first()
        if customer:
            return f"Customer is {customer.first_name} {customer.last_name}"    
        else:
            return "Customer for the specified id doesn't exist"    
    
    def restaurant(self):
        # Returns the restaurant instance for this review
        restaurant = session.query(Restaurant).join(Review).filter(Review.id == self.id).first()
        if restaurant:
            return f"Restaurant is {restaurant.name}"
        return f"Restaurant for the specified id doesn't exist"
    
    def full_review(self):
        return f"Review for {self.restaurants.name} by {self.customers.full_name()}: {self.rating} stars."
        
             
engine = create_engine('sqlite:///restaurants.db')            
Session = sessionmaker(bind=engine)
session = Session()


## ########################### #
# Aggregate and Relationship Methods
# ########################### #

# CUSTOMER FULL_NAME
# resinstance = Customer('naruto', 'uzumaki')
# rev = resinstance.full_name()
# print(rev)

# CUSTOMER FAVOURITE_RESTAURANT
# customer = session.query(Customer).filter_by(id=1).first()
# rev = customer.favorite_restaurant()
# if rev:
#     print(f"favorite restaurant is {rev.name}")
# else:
#     print("no favorite restaurant found")    

# CUSTOMER ADD REVIEW
# customer = Customer('kisuke', 'urahara')
# session.add(customer)
# session.commit()
# restaurant_id = 11
# rating  = 8
# customer.add_review(rating, restaurant_id)
# customer = session.query(Customer).filter_by(id=3).first()
# restaurant = session.query(Restaurant).filter_by(id=5).first()
# rating = 7
# review = Review(rating, restaurant.id, customer.id)
# result = customer.add_review(rating, restaurant)
# print(result)


# result = restaurant.reviews()
# print(result)

# DELETE REVIEW 
# customer = session.query(Customer).filter_by(id=17).first()
# restaurant = session.query(Restaurant).filter_by(id=6).first()
# customer.delete_reviews(restaurant)

# REVIEW
# REVIEW FULL REVIEW
# review = session.query(Review).filter_by(id=5).first()
# result = review.full_review()
# print(result)

# RESTAURANT
# FANCIEST RESTAURANT
# restaurant = session.query(Restaurant).all()
# restaurant = Restaurant.fanciest()

# ALL REVIEWS
# restaurant = session.query(Restaurant).filter_by(id=4).first()
# reviews = restaurant.all_reviews()
# print(reviews)

# ########################### #
# OBJECT RELATIONAL MAPPING
# ########################### #
# CUSTOMER REVIEWS
# reviews = session.query(Customer).filter_by(id=3).first()
# result = reviews.reviews()
# print(result)

# CUSTOMER RESTAURANTS
# restaurant = session.query(Customer).filter_by(id=3).first()
# result = restaurant.customer_restaurants()
# print(result)

# RESTAURANT REVIEWS
# restaurant = session.query(Restaurant).filter_by(id=3).first()
# result = restaurant.reviews()
# print(result)

# RESTAURANT CUSTOMERS
restaurant = session.query(Restaurant).filter_by(id=3).first()
result = restaurant.restaurant_customers()
print(result)

# REVIEW RESTAURANT
# review = session.query(Review).filter_by(id=2).first()
# result = review.restaurant()
# print(result)

# REVIEW CUSTOMER
# review = session.query(Review).filter_by(id=2).first()
# rev = review.customer()
# print(rev)
    