# Automated Probabilistic Choice Abstraction

This code is meant to automate the application of Probabilistic Choice Abstraction. It is not currently complete and may not function properly in some cases.

## Usage
The script can be invoked by calling python followed by the path to `src/convert.py`. Following that, two arguments are required: The path to the jani file to be converted, and the filename (or path) for where the converted jani file should be written.

And example command is listed below:
`python src/convert.py /path/to/original/jani/file /path/to/converted/jani`

## Obtaining a JANI file

This script can only convert models in the JANI format. To convert a modest file into a JANI file, run the following:
`/path/to/modest/executable/ moconv /path/to/modest/file -F -O /path/for/jani/file`

## Visualizing autamata
It may be useful to visualize the automata before and after conversion in order to determine if the conversion worked. Use the following command to generate a PNG file for a particular JANI model:
`/path/to/modest/executable/ mosta MODEL_PATH.jani --dot png IMAGE_PATH.png -O IMAGE_PATH.png`

Generating an image for both the original and abstracted model can help visualize the result of using the tool. 

## Testing

The overall goal of the tool is to have the results of checking the properties be the same, but with fewer states required. To check the properties for a JANI file, use:
`/path/to/modest/executable/ mcsta MODEL_PATH.jani`

Running this command on the original and converted JANI files will yield the same probabilities for each property when the code is working properly.


## Examples

There are several toy models in the `models` folder, along with their converted versions. Toy models 1-4 work with the current version of the tool, but other models are not guaranteed to work at this time.