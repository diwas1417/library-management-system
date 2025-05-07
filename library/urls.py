from django.urls import path
from .views import BookListView, IssueBookView, home, login_view, login_page, register_view, register_page, logout_view, BorrowHistoryView, ReturnBookView, AddBookView, EditBookView, admin_books_page, UserListView, PromoteUserView, manage_roles_page, GenreListView, BookDetailView, DeleteBookView

urlpatterns = [
    path('', home, name='home'),
       path('login/', login_page, name='login-page'),
    path('register/', register_page, name='register-page'),
    path('login/api/', login_view, name='login'),
    path('register/api/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/issue/', IssueBookView.as_view(), name='issue-book'),
    path('borrow/history/', BorrowHistoryView.as_view(), name='borrow-history'),
    path('books/return/', ReturnBookView.as_view(), name='return-book'),
    path('dashboard/add-book/', AddBookView.as_view(), name='add-book'),
    path('dashboard/edit-book/<uuid:book_id>/', EditBookView.as_view(), name='edit-book'),
    path('dashboard/manage-books/', admin_books_page, name='admin-books-page'),
    path('dashboard/users/', UserListView.as_view(), name='user-list'),
    path('dashboard/promote-user/', PromoteUserView.as_view(), name='promote-user'),
    path('dashboard/manage-roles/', manage_roles_page, name='manage-roles-page'),
    path('dashboard/genres/', GenreListView.as_view(), name='genre-list'),
    path('books/<uuid:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('dashboard/edit-book/<uuid:book_id>/', EditBookView.as_view(), name='edit-book'),
    path('dashboard/delete-book/<uuid:book_id>/', DeleteBookView.as_view(), name='delete-book'),
]
