# MWM

Might-Work MUD

## Purpose

If you've followed my Github profile you'll know I've tried lots of different ways to make lots of different game servers, with the primary focus being on text and audio. I recently started playing [A Hero's Call](https://www.kickstarter.com/projects/1112411595/a-heros-call-an-accessible-fantasy-rpg) which reminded me of when I used to play [Valhalla MUD](http://www.valhalla.com/) which was awesome. Anyways, the long and the short of it is that now I have as good as been banned from Valhalla, I'd quite like to make something that works similarly.

There is of course:

* [Circle MUD](http://www.circlemud.org/)
* [tbaMUD](https://github.com/tbamud/tbamud)
* [Evennia](https://github.com/evennia/evennia)

And probably others, but I thought maybe I could do something different. For anyone who knows me, that translates loosely to:

> I don't understand how they work, and I'd rather write my own than read documentation.

## Differences

MWM uses [Python](https://www.python.org)'s [argparse](https://docs.python.org/3/library/argparse.html) module for the majority of it's commands. This gives you all the flexibility that you'd get writing any other console program. As that is basically what a MUD is, I thought why not?

Anyone who complains that my method spoils immersion is completely right... That said, *I don't understand that* doesn't exactly keep me in the spirit of the thing either, and at least MWM commands have easy to read autogenerated help files which you'd probably end up writing anyway.

## Beatures

MWM has support for command substitutions. By default:

<dl>
  <dt>'</dt>
  <dd>say</dd>
  <dt>:</dt>
  <dd>emote</dd>
  <dt>;</dt>
  <dd>eval</dd>
  <dt>`</dt>
  <dd>exec</dd>
</dl>

These are configurable on a per-instance basis with the configuration module (which has yet to gain a front end).

While MWM uses a flat file for persistent storage, an in-memory [SQLite](http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html) database is used while the game is running. This gives us greater control over pretty much everything as complex queries can be formed to ask questions about the state of the server.

Sure: `[room for room in rooms.values() if room.light is True]` would work, but `Room.query(light=True)` is less typing and more concise I feel.

## Commands

There are plenty of commands already written which serve to document how the commands system works, but I thought I'd include a step-by-step guide anyway to hopefully outline any pitfalls.

### Getting Started

As I said before, commands use the [argparse](https://docs.python.org/3/library/argparse.html) module. In fact, `commands.base.Command` is a direct subclass of `argparse.ArgumentParser`. For instructions your first port of call should be the [argparse documentation](https://docs.python.org/3/library/argparse.html).

It is a good idea to put your command either in one of the existing command files in the `commands` directory or create a new file there.

### Importing

```
from .base import Command
```

Now you can subclass Command with no worries. Remember to include a docstring as this will be used as the description for the new command.

```
class Test(Command):
    """This is a test command which can be invoked by typing test when logged into the game."""
```

By default, `self.prog` is set to the name of the class with all underscores replaced with dashes, and converted to lower case.

```
class Test_Command(Command):
    """You can type test-command when logged into the game to invoke this command."""
```

### Initialisation

Instead of overriding `__init__` (which requires more boilerplate than I like), provide an `on_init` method.

```
class Test(Command):
    """This is a test command."""

    def on_init(self):
        """Initialisation stuff goes here."""
```

If you want your command to be accessible by more than one name, you can add as many aliases as you like to the `aliases` list.

```
class Test(Command):
    """This is a test command which can be invoked by typing test when logged into the game."""
    def on_init(self):
        """Initialisation stuff goes here."""
        # Add one at a time:
        self.aliases.append('@test')
        self.aliases.append('@test-command')
        # Or add multiple aliases:
        self.aliases.extend(['@command-test', 'command-test', 'test-command'])
```

### Adding Arguments

You can add arguments using the standard argparse machinary.

```
class Open(Command):
    """Open something."""
    def on_init(self):
        self.add_argument('thing', help='The thing to open')
```

### Do Something

Now we know how to add arguments, let's write a meaningful command. Let's start like real programmers with a simple `hello world` example. We add code with the `func` method.

```
class Hello(Command):
    """Say hello world to the character."""
    def func(self, character, args, text):
        """Say hello and be done with it."""
        character.notify('Hello world.')
```

Simple, but effective! Let's talk about the arguments:

<dl>
  <dt>character</dt>
  <dd>A `character` instance. You can safely assume this is a fully authenticated character, with a valid `connection` property which you can manipulate with [Twisted](https://twistedmatrix.com/)'s normal idioms.</dd>
  <dt>args</dt>
  <dd>The result of calling the `parse_args` method of your command. Don't worry, the `exit` method has been overridden to ensure your command will never raise `SystemExit`.</dd>
  <dt>text</dt>
  <dd>The text of your command, minus the command portion.</dd>
</dl>

### Exceptions

Instances of `commands.base.command` may raise `commands.base.CommandError` errors. This exception is used in lieu of `sys.exit` for `commands.base.Command.exit`.

## Socials

Socials are possible with MWM using the [emote-utils](https://pypi.python.org/pypi/emote_utils/1.0.2) package. The package's contents has been wrapped in the following ways:

- An instance of `emote_utils.SocialsFactory` is provided as `socials.socials`.
- All social suffixes should be left in the `socials.py` file.
- You can use `db.characters.Character.do_social` to have a given `character` instance perform a social.

### Performing Socials

You can use `do_social` as follows:

```
character.do_social('%1n smile%1s.')
character.do_social('%1n smile%1s at %2n.', _others=[other])
```

You can pass arbitrary keyword arguments to the underlying `get_strings` method as extra keyword arguments to `do_social`. For instance:

```
character.do_social('%1n say%1s: "{text}"', text='This is what I say.')
```

At the basic level, `do_social` gives you a perspectives list which has the character in the first position, extended by `_others` if necessary, and all extra arguments passed directly to `socials.get_strings`.

Moreover, the perspectives list is iterated over by `do_social` to send the correct string to the relevant recipient so you don't have to.

## Testing

While there is some test coverage using [pytest](https://pytest.org/), I haven't written tests for everything... In fairness actually, the test coverage is pretty rubbish; feel free to submit pull requests if this worries you (it does me).

### t.py

For everything else there is t.py. This little script loads configuration and database and gives you some handy globals. We will use this in the next section.

## Database

As previously stated, the database is where the bulk of the magic (no pun intended) happens.

### What's available

Instead of me writing a list here, execute the file table.py to see what is available.
