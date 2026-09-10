"""
Library Management System
--------------------------
A console-based Python project built for the Final Internship Project (Week 6).

Demonstrates:
- Python Fundamentals (variables, I/O, operators, type casting)
- Conditional Statements & Loops
- Functions
- Data Structures (list, dict)
- File Handling (JSON persistence)
- Exception Handling
- Object-Oriented Programming (Classes, Objects, Constructors,
  Inheritance, Polymorphism, Encapsulation & Abstraction)
"""

import json
import os
from datetime import date


# ---------------------------------------------------------------------
# File paths used for persistent storage (File Handling)
# ---------------------------------------------------------------------
BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"


# ---------------------------------------------------------------------
# ABSTRACTION / BASE CLASS
# ---------------------------------------------------------------------
class Person:
    """Base class representing a generic person in the system.
    Demonstrates Encapsulation (private attributes with getters)
    and forms the base for Inheritance."""

    def __init__(self, name, contact):
        self._name = name          # protected attribute (encapsulation)
        self.__contact = contact   # private attribute (encapsulation)

    @property
    def name(self):
        return self._name

    @property
    def contact(self):
        return self.__contact

    def display_info(self):
        """Meant to be overridden by subclasses (abstraction)."""
        raise NotImplementedError("Subclasses must implement display_info()")


# ---------------------------------------------------------------------
# INHERITANCE + POLYMORPHISM
# ---------------------------------------------------------------------
class Member(Person):
    """A library member. Inherits from Person."""

    def __init__(self, member_id, name, contact):
        super().__init__(name, contact)
        self.member_id = member_id
        self.borrowed_books = []   # list data structure

    def display_info(self):        # polymorphism: overrides Person.display_info
        return (f"Member ID: {self.member_id} | Name: {self.name} | "
                f"Contact: {self.contact} | Borrowed: {len(self.borrowed_books)} book(s)")

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact": self.contact,
            "borrowed_books": self.borrowed_books,
        }


class Librarian(Person):
    """A librarian/admin user. Also inherits from Person."""

    def __init__(self, name, contact, staff_id):
        super().__init__(name, contact)
        self.staff_id = staff_id

    def display_info(self):        # polymorphism: different implementation
        return f"Librarian: {self.name} (Staff ID: {self.staff_id})"


# ---------------------------------------------------------------------
# Book class (Encapsulation)
# ---------------------------------------------------------------------
class Book:
    def __init__(self, book_id, title, author, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.total_copies = int(copies)
        self.available_copies = int(copies)

    def is_available(self):
        return self.available_copies > 0

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    def __str__(self):
        status = "Available" if self.is_available() else "Not Available"
        return (f"[{self.book_id}] '{self.title}' by {self.author} | "
                f"Copies: {self.available_copies}/{self.total_copies} | {status}")


# ---------------------------------------------------------------------
# Custom Exceptions (Exception Handling)
# ---------------------------------------------------------------------
class BookNotAvailableError(Exception):
    pass


class RecordNotFoundError(Exception):
    pass


# ---------------------------------------------------------------------
# Library class - the core manager (uses Functions, Loops, Data Structures,
# File Handling, Exception Handling)
# ---------------------------------------------------------------------
class Library:
    def __init__(self):
        self.books = {}      # dict: book_id -> Book object
        self.members = {}    # dict: member_id -> Member object
        self.load_data()

    # ---------------- File Handling ----------------
    def load_data(self):
        """Load books and members from JSON files, if they exist."""
        try:
            if os.path.exists(BOOKS_FILE):
                with open(BOOKS_FILE, "r") as f:
                    data = json.load(f)
                    for b in data:
                        book = Book(b["book_id"], b["title"], b["author"], b["total_copies"])
                        book.available_copies = b["available_copies"]
                        self.books[book.book_id] = book

            if os.path.exists(MEMBERS_FILE):
                with open(MEMBERS_FILE, "r") as f:
                    data = json.load(f)
                    for m in data:
                        member = Member(m["member_id"], m["name"], m["contact"])
                        member.borrowed_books = m["borrowed_books"]
                        self.members[member.member_id] = member
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠ Warning: could not fully load saved data ({e}). Starting fresh where needed.")

    def save_data(self):
        """Save current books and members to JSON files."""
        with open(BOOKS_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.books.values()], f, indent=4)
        with open(MEMBERS_FILE, "w") as f:
            json.dump([m.to_dict() for m in self.members.values()], f, indent=4)

    # ---------------- Book Management ----------------
    def add_book(self, book_id, title, author, copies):
        if book_id in self.books:
            print("A book with this ID already exists.")
            return
        self.books[book_id] = Book(book_id, title, author, copies)
        self.save_data()
        print(f"Book '{title}' added successfully.")

    def view_books(self):
        if not self.books:
            print("No books in the library yet.")
            return
        print("\n--- Library Catalogue ---")
        for book in self.books.values():   # loop over data structure
            print(book)

    # ---------------- Member Management ----------------
    def add_member(self, member_id, name, contact):
        if member_id in self.members:
            print("A member with this ID already exists.")
            return
        self.members[member_id] = Member(member_id, name, contact)
        self.save_data()
        print(f"Member '{name}' registered successfully.")

    def view_members(self):
        if not self.members:
            print("No members registered yet.")
            return
        print("\n--- Registered Members ---")
        for member in self.members.values():
            print(member.display_info())      # polymorphic call

    # ---------------- Borrow / Return (Exception Handling) ----------------
    def borrow_book(self, member_id, book_id):
        try:
            if member_id not in self.members:
                raise RecordNotFoundError(f"Member ID '{member_id}' not found.")
            if book_id not in self.books:
                raise RecordNotFoundError(f"Book ID '{book_id}' not found.")

            book = self.books[book_id]
            member = self.members[member_id]

            if not book.is_available():
                raise BookNotAvailableError(f"'{book.title}' has no available copies right now.")

            book.available_copies -= 1
            member.borrowed_books.append({"book_id": book_id, "date": str(date.today())})
            self.save_data()
            print(f"'{book.title}' issued to {member.name} successfully.")

        except RecordNotFoundError as e:
            print(f"Error: {e}")
        except BookNotAvailableError as e:
            print(f"Error: {e}")

    def return_book(self, member_id, book_id):
        try:
            if member_id not in self.members:
                raise RecordNotFoundError(f"Member ID '{member_id}' not found.")
            member = self.members[member_id]

            record = next((r for r in member.borrowed_books if r["book_id"] == book_id), None)
            if record is None:
                raise RecordNotFoundError("This member has not borrowed this book.")

            member.borrowed_books.remove(record)
            if book_id in self.books:
                self.books[book_id].available_copies += 1
            self.save_data()
            print("Book returned successfully.")

        except RecordNotFoundError as e:
            print(f"Error: {e}")


# ---------------------------------------------------------------------
# Menu-driven Command Line Interface (Functions, Conditionals, Loops, I/O)
# ---------------------------------------------------------------------
def print_menu():
    print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
    print("1. Add Book")
    print("2. View All Books")
    print("3. Register Member")
    print("4. View All Members")
    print("5. Borrow Book")
    print("6. Return Book")
    print("7. Exit")


def get_int_input(prompt):
    """Helper function with exception handling for type casting."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def main():
    library = Library()

    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            book_id = input("Book ID: ").strip()
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            copies = get_int_input("Number of copies: ")
            library.add_book(book_id, title, author, copies)

        elif choice == "2":
            library.view_books()

        elif choice == "3":
            member_id = input("Member ID: ").strip()
            name = input("Name: ").strip()
            contact = input("Contact number: ").strip()
            library.add_member(member_id, name, contact)

        elif choice == "4":
            library.view_members()

        elif choice == "5":
            member_id = input("Member ID: ").strip()
            book_id = input("Book ID: ").strip()
            library.borrow_book(member_id, book_id)

        elif choice == "6":
            member_id = input("Member ID: ").strip()
            book_id = input("Book ID: ").strip()
            library.return_book(member_id, book_id)

        elif choice == "7":
            print("Thank you for using the Library Management System. Goodbye!")
            break

        else:
            print("Invalid choice. Please select between 1-7.")


if __name__ == "__main__":
    main()