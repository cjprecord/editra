" Example for use of GNU gettext.
  Copyright (C) 2003 Free Software Foundation, Inc.
  This file is in the public domain.

  Source code of the GNU Smalltalk program.
"

"Unfortunately the PackageLoader method fileInPackage: is extra verbose:
 It outputs 'Loading package I18N'. This will be fixed in smalltalk-2.2.

PackageLoader fileInPackage: 'I18N' !

In the meantime, we use this workaround."

| saved sink |
saved := Transcript message.
sink := WriteStream with: String new.
Transcript message: sink -> #nextPutAll:.
PackageLoader fileInPackage: 'I18N'.
Transcript message: saved.
!

Object subclass: #Main   Window turtleWindow: 'Turtle Graphics'.
      Turtle
          defaultNib: 2;
          foreColor: ClrDarkgray;
          home;
          go: 100;
          turn: 120;
          go: 100;
          turn: 120;
          go: 100;
          turn: 120
