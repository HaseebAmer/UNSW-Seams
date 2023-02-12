# import pytest
# from src.auth import auth_login_v1, auth_register_v1
# from src.other import clear_v1
# from src.error import InputError

# # testing case where registration works and returns the correct id
# def test_register_working():
#     clear_v1()

#     rego_return = auth_register_v1("last123@gmail.com", "hello123", "Franz", "Beckenbauer")
#     auth_user_id1 = rego_return['auth_user_id']

#     login_return = auth_login_v1("last123@gmail.com", "hello123")
#     auth_user_id2 = login_return['auth_user_id']
#     assert auth_user_id1 == auth_user_id2

# # test auth_user_id is different for different users
# def different_auth_id():
#     clear_v1()

#     return_value1 = auth_register_v1("idontknow@gmail.com", "hello5678", "Ben", "Mendy")
#     auth_user_id1 = return_value1['auth_user_id']

#     return_value2 = auth_register_v1("bravenewworld@gmail.com", "dystopia", "Mason", "Greenwood")
#     auth_user_id2 = return_value2['auth_user_id']

#     assert auth_user_id1 != auth_user_id2

# # test case where the email is invalid
# def test_register_invalid_email():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first.com", "helloworld", "John", "Doe")
#     with pytest.raises(InputError):
#         assert auth_register_v1("first/last@gmail.com", "uranus", "John", "Franklin")
#     with pytest.raises(InputError):
#         assert auth_register_v1("    @gmail.com", "uranus", "John", "Franklin")
#     with pytest.raises(InputError):
#         assert auth_register_v1("first&last@gmail.com", "uranus", "John", "Doe")
#     with pytest.raises(InputError):
#         assert auth_register_v1("", "uranus", "John", "Doe")

# # test case where another user is already using that email
# def test_register_email_in_use():
#     clear_v1()
#     auth_register_v1("first@gmail.com", "hello123", "Eric", "Khan")
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "helloworld", "Frank", "Jong")

# # test case where password is too short
# def test_register_short_password():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "aaaa", "Eric", "Khan")

# # test case where the first name is too short (empty)
# def test_register_short_firstname():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "helloworld", "", "Jong")

# # test case where the surname is too short (empty)
# def test_register_short_surname():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "helloworld", "Frank", "")

# # test case where the first name is too long (> 50 characters)
# def test_register_long_firstname():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "helloworld", "aaaabbbbccccddddeeeeffffgggghhhhiiiijjjjkkkkllllmmmm", "Ocean")

# # test case where the surname is too long (> 50 characters)
# def test_register_long_surname():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_register_v1("first@gmail.com", "helloworld", "Bob", "aaaabbbbccccddddeeeeffffgggghhhhiiiijjjjkkkkllllmmmm")

# # testing cases where the email entered does not belong to a user
# def test_login_email():
#     clear_v1()
#     auth_register_v1("first@gmail.com", "helloworld", "Alex", "Ferguson")
#     with pytest.raises(InputError):
#         assert auth_login_v1("invalid_email@gmail.com", "helloworld")

# # testing case where the password entered is incorrect
# def test_login_pass():
#     clear_v1()
#     auth_register_v1("third@gmail.com", "hello123", "Trent", "Arnold")
#     with pytest.raises(InputError):
#         assert auth_login_v1("third@gmail.com", "Hello123")

# # test case where the email inputted is invalid
# def test_login_invalid_email():
#     clear_v1()
#     with pytest.raises(InputError):
#         assert auth_login_v1("first.com", "hello123")
#     with pytest.raises(InputError):
#         assert auth_login_v1("first/last@gmail.com", "random")
