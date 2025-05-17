import csv
import bcrypt
import datetime
import os
import argparse
from dataclasses import dataclass
from typing import List, Optional

# Paths to CSV files
data_dir = './data/'
books_file = os.path.join(data_dir, 'books.csv')
members_file = os.path.join(data_dir, 'members.csv')
loans_file = os.path.join(data_dir, 'loans.csv')

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)

# Create empty CSV files if they don't exist
for file in [books_file, members_file, loans_file]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            pass

# Data Classes
@dataclass
class Book:
    ISBN: str
    Title: str
    Author: str
    CopiesTotal: int
    CopiesAvailable: int

@dataclass
class Member:
    MemberID: str
    Name: str
    PasswordHash: str
    Email: str
    JoinDate: str

@dataclass
class Loan:
    LoanID: str
    MemberID: str
    ISBN: str
    IssueDate: str
    DueDate: str
    ReturnDate: str = ''

# Helper Functions for CSV Operations
# Helper Functions for CSV Operations
def load_books() -> List[Book]:
    with open(books_file, 'r') as f:
        reader = csv.reader(f)
        # Convert CopiesTotal and CopiesAvailable to int
        return [Book(row[0], row[1], row[2], int(row[3]), int(row[4])) for row in reader]



def save_books(books: List[Book]):
    with open(books_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for book in books:
            writer.writerow([book.ISBN, book.Title, book.Author, book.CopiesTotal, book.CopiesAvailable])


def load_members() -> List[Member]:
    with open(members_file, 'r') as f:
        reader = csv.reader(f)
        return [Member(*row) for row in reader]


def save_members(members: List[Member]):
    with open(members_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for member in members:
            writer.writerow([member.MemberID, member.Name, member.PasswordHash, member.Email, member.JoinDate])


def load_loans() -> List[Loan]:
    with open(loans_file, 'r') as f:
        reader = csv.reader(f)
        return [Loan(*row) for row in reader]


def save_loans(loans: List[Loan]):
    with open(loans_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for loan in loans:
            writer.writerow([loan.LoanID, loan.MemberID, loan.ISBN, loan.IssueDate, loan.DueDate, loan.ReturnDate])

# Register a new member
def register_member():
    members = load_members()
    member_id = input("Enter Member ID: ")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    password = input("Enter Password: ")
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    join_date = datetime.date.today().strftime('%Y-%m-%d')
    members.append(Member(member_id, name, hashed_password, email, join_date))
    save_members(members)
    print(f"✔ Member '{name}' registered successfully!")

# Add a new book
def add_book():
    books = load_books()
    isbn = input("Enter ISBN: ")
    title = input("Enter Title: ")
    author = input("Enter Author: ")
    copies_total = int(input("Enter Total Copies: "))
    books.append(Book(isbn, title, author, copies_total, copies_total))
    save_books(books)
    print(f"✔ Book '{title}' added successfully!")

# Issue a book
def issue_book():
    loans = load_loans()
    books = load_books()
    isbn = input("Enter ISBN to issue: ")
    member_id = input("Enter Member ID: ")
    book = next((b for b in books if b.ISBN == isbn and int(b.CopiesAvailable) > 0), None)
    if book:
        book.CopiesAvailable -= 1
        issue_date = datetime.date.today().strftime('%Y-%m-%d')
        due_date = (datetime.date.today() + datetime.timedelta(days=14)).strftime('%Y-%m-%d')
        loan_id = str(len(loans) + 1)
        loans.append(Loan(loan_id, member_id, isbn, issue_date, due_date))
        save_books(books)
        save_loans(loans)
        print(f"✔ Book issued. Due on {due_date}.")
    else:
        print("❌ Book not available or ISBN not found.")

# Return a book
def return_book():
    loans = load_loans()
    books = load_books()
    loan_id = input("Enter Loan ID to return: ")
    loan = next((l for l in loans if l.LoanID == loan_id and l.ReturnDate == ''), None)
    if loan:
        loan.ReturnDate = datetime.date.today().strftime('%Y-%m-%d')
        book = next(b for b in books if b.ISBN == loan.ISBN)
        book.CopiesAvailable += 1
        save_books(books)
        save_loans(loans)
        print(f"✔ Book returned successfully.")
    else:
        print("❌ Invalid Loan ID or book already returned.")

# View overdue loans
def view_overdue():
    loans = load_loans()
    today = datetime.date.today().strftime('%Y-%m-%d')
    overdue_loans = [l for l in loans if l.ReturnDate == '' and l.DueDate < today]
    if overdue_loans:
        print("\n=== Overdue Loans ===")
        for loan in overdue_loans:
            print(f"Loan ID: {loan.LoanID}, Member ID: {loan.MemberID}, ISBN: {loan.ISBN}, Due Date: {loan.DueDate}")
    else:
        print("✔ No overdue loans.")

# Librarian Menu
def librarian_menu():
    while True:
        print("\n=== Librarian Dashboard ===")
        print("1. Add Book")
        print("2. Register Member")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. Overdue List")
        print("6. Logout")
        choice = input("> ")

        if choice == '1':
            add_book()
        elif choice == '2':
            register_member()
        elif choice == '3':
            issue_book()
        elif choice == '4':
            return_book()
        elif choice == '5':
            view_overdue()
        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("❌ Invalid choice. Please try again.")

# Entry Point
if __name__ == '__main__':
    bcrypt_version = bcrypt.__version__
    print(f"📚 Library Management System (bcrypt v{bcrypt_version})")
    librarian_menu()
