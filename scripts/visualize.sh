#!/bin/bash
path_with_ext=$1
path_no_ext=${path_with_ext%.jani}
name_with_ext=${path_with_ext##*/}
name_no_ext=${path_no_ext##*/}

echo ""
echo "Converting $name_with_ext to .dot $name_no_ext.dot"
echo "modest mosta $path_with_ext -O $name_no_ext.dot"
modest mosta $path_with_ext -O $name_no_ext.dot
echo "Conversion to .dot complete"

echo ""
echo "Converting $name_no_ext.dot to png $name_no_ext.png"
echo "dot -Tpng $name_no_ext.dot -o $name_no_ext.png"
dot -Tpng $name_no_ext.dot -o $name_no_ext.png

echo ""
echo "Conversion to .png Complete"
echo "Creating folder $name_no_ext"
mkdir $name_no_ext
echo "Moving files to $name_no_ext"
mv $path_with_ext $name_no_ext
mv $name_no_ext.dot $name_no_ext
mv $name_no_ext.png $name_no_ext
mv workfile.txt $name_no_ext
mv datafile.txt $name_no_ext
echo "Exiting script"
echo ""
