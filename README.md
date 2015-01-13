ccl
===

- Processes a binary (black and white) image to find connected regions
- Compares the color of a pixel to that of its surroundings
- If neighboring pixels are the same color they have the same label
- Uses an equivalence table to reduce number of labels
- In the output image each connected area has a different color
- Usage: `python ccl.py [-sf] –i <input_file> [-o <output_file>]`
- `-sf` flag is for a size filter, meaning a filter is applied to remove small pixel regions
- Output is either shown or saved to a file with `-o` flag

Input Image | Output Image
----------- | ------------
![alt tag](http://i.imgur.com/swVbHQC.png) | ![alt tag](http://i.imgur.com/oKAcj9Y.png)
![alt tag](http://i.imgur.com/TapGARy.png) | ![alt tag](http://i.imgur.com/K1po3Ef.png)
![alt tag](http://i.imgur.com/YXJWrI7.png) | ![alt tag](http://i.imgur.com/Li70Qwe.png)
![alt tag](http://i.imgur.com/YXJWrI7.png) | ![alt tag](http://i.imgur.com/OcQMMfR.png)Size filter
