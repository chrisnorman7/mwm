"""Provides the socials factory."""

from emote_utils import SocialsFactory

__all__ = ['socials']

socials = SocialsFactory()


@socials.suffix('n', 'name')
def get_name(obj, suffix):
    """"you" or your name."""
    return 'you', obj.name


@socials.suffix('s')
def get_s(obj, suffix):
    """"" or "s"."""
    return '', 's'


@socials.suffix('e', 'es')
def get_es(obj, suffix):
    """"" or "es"."""
    return '', 'es'


@socials.suffix('y', 'ies')
def get_y(obj, suffix):
    """"y" or "ies"."""
    return 'y', 'ies'


@socials.suffix('are', 'is')
def are(obj, suffix):
    """"are" or "is"."""
    return ('are', 'is')


@socials.suffix('ss', 'your')
def your(obj, suffix):
    """"your" or "name's"."""
    return ('your', f"{obj.get_name()}'s")


@socials.suffix('he', 'she', 'it', 'subjective')
def subjective(obj, suffix):
    """"you" or the object's subjective pronoun."""
    return ('you', obj.get_gender().subjective)


@socials.suffix('him', 'her', 'o', 'objective')
def objective(obj, suffix):
    """"you" or the object's objective pronoun."""
    return ('you', obj.get_gender().objective)


@socials.suffix('his', 'its', 'p', 'pa')
def possessive_adjective(obj, suffix):
    """"your" or the object's possessive adjective."""
    return ('your', obj.get_gender().possessive_adjective)


@socials.suffix('hers', 'pn')
def possessive_noun(obj, suffix):
    """"your" or the object's possessive noun. Exactly the same as the your and
    ss suffixes."""
    return your(obj, suffix)


@socials.suffix('himself', 'herself', 'itself', 'r', 'reflexive')
def reflexive(obj, suffix):
    """"yourself" or the object's reflexive pronoun."""
    return ('yourself', obj.get_gender().reflexive)
