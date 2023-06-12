#!/usr/bin/env fish
set dir (realpath (dirname (status current-filename)))

set failsh $dir/fail.sh
set succeedsh $dir/succeed.sh

rm -rf $dir/path
mkdir $dir/path

for command in (cat $dir/optical_write_test.garbled.sh | awk '{ print $1 }' | sort | uniq | tail -n+2)
    echo $dir/path/$command
    ln -s $succeedsh $dir/path/$command
end
