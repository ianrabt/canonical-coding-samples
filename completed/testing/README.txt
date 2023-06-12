Just a quick script to let you test various failure conditions, and compare
python and sh behavior -- not necessary for the full submission: this "testing"
directory can be ignored

e.g.
  testing/gen-path.fish
  PATH=testing/path/:$PATH ./optical_write_test.sh
  PATH=testing/path/:$PATH ./optical_write_test.py
