from rest_framework.test import APIClient
import pytest
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.parametrize('course', ({'id': 1, 'name': 'Builder. Bodybuilder', 'students': [i for i in range(5)]},
                                    {'id': 2, 'name': 'Magical Pony Land', 'students': [i for i in range(20)]}))
def test_specific_settings_true(course, settings):
    true = settings.MAX_STUDENTS_PER_COURSE >= len(course['students'])
    assert true


@pytest.mark.xfail
@pytest.mark.parametrize('course', ({'id': 1, 'name': 'Builder. Bodybuilder', 'students': [i for i in range(200)]},
                                    {'id': 2, 'name': 'Magical Pony Land', 'students': [i for i in range(21)]}))
def test_specific_settings_false(course, settings):
    true = settings.MAX_STUDENTS_PER_COURSE >= len(course['students'])
    assert true


@pytest.mark.django_db
def test_first_course(client, students_factory, courses_factory):
    students = students_factory(_quantity=10)
    course = courses_factory(_quantity=1, students=students)
    response = client.get('http://127.0.0.1:8000/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == course[0].name
    assert data[0]['id'] == course[0].id


@pytest.mark.django_db
def test_many_courses(client, students_factory, courses_factory):
    students = students_factory(_quantity=10)
    course = courses_factory(_quantity=2, students=students)
    response = client.get('http://127.0.0.1:8000/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    for i, c in enumerate(data):
        assert c['name'] == course[i].name
        assert c['id'] == course[i].id


@pytest.mark.django_db
def test_courses_id_filtration(client, students_factory, courses_factory):
    students = students_factory(_quantity=10)
    course = courses_factory(_quantity=200, students=students)
    response = client.get(f'http://127.0.0.1:8000/api/v1/courses/?id={course[2].id}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['id'] == course[2].id
    assert data[0]['name'] == course[2].name


@pytest.mark.django_db
def test_courses_name_filtration(client, students_factory, courses_factory):
    students = students_factory(_quantity=10)
    course = courses_factory(_quantity=200, students=students)
    response = client.get(f'http://127.0.0.1:8000/api/v1/courses/?name={course[156].name}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['id'] == course[156].id
    assert data[0]['name'] == course[156].name


@pytest.mark.django_db
def test_course_post(client, students_factory):
    students = students_factory(_quantity=10)
    name = 'Fitnessstudio'
    response = client.post('http://127.0.0.1:8000/api/v1/courses/',
                           data={'id': 1,
                                 'name': name,
                                 'students': [s.id for s in students]})
    assert response.status_code == 201


@pytest.mark.django_db
def test_course_patch(client, students_factory, courses_factory):
    students = students_factory(_quantity=10)
    course = courses_factory(_quantity=200, students=students)
    response = client.patch(f'http://127.0.0.1:8000/api/v1/courses/{course[43].id}/',
                            data={'students': [s.id for s in students[1:6]]})
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_delete(client, students_factory, courses_factory):
    students = students_factory(_quantity=15)
    course = courses_factory(_quantity=200, students=students)
    response = client.delete(f'http://127.0.0.1:8000/api/v1/courses/{course[199].id}/')
    assert response.status_code == 204
    response = client.delete(f'http://127.0.0.1:8000/api/v1/courses/{course[199].id}/')
    assert response.status_code == 404
