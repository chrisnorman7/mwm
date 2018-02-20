from pytest import raises
from intercepts import Intercept


class TestConnection:
    """Stop AttributeError from happening."""


con = TestConnection()


class Done(Exception):
    """Test passes."""


def done_single_line(text):
    assert text == 'testing'
    raise Done()


def done_multi_line(text):
    assert text == 'hello\nworld'
    raise Done()


def done_args(text, first, second, hello=None):
    assert text == 'test'
    assert first == 1
    assert second == 2
    assert hello == 'world'
    raise Done()


def test_single_line():
    i = Intercept(done_single_line, connection=con)
    with raises(Done):
        i.feed('testing')


def test_multi_line():
    i = Intercept(done_multi_line, multiline=True, connection=con)
    i.feed('hello')
    i.feed('world')
    with raises(Done):
        i.feed(i.end)


def test_args():
    i = Intercept(
        done_args, args=(1, 2), kwargs=dict(hello='world'), connection=con
    )
    with raises(Done):
        i.feed('test')
