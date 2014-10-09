import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt

class BinaryImage:
	def __init__(self, img):
		self.img = img
		ret,self.thresh = cv2.threshold(self.img,127,255,cv2.THRESH_BINARY)
		self.rows,self.cols = self.thresh.shape
		self.background = 0
		self.label_counter = 0
		self.equiv_table = {}
		self.labeled_image = LabeledImage(self.rows, self.cols, self.background)

	def ccl_first(self):
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				current = Pixel(self.thresh.item(i,j))
				if current.is_not_label(self.background):
					left,upper = self.get_neighbors(i,j)
					self.label_pixel(current, left, upper)
				self.labeled_image.label_pixel(i, j, current.label)

	def ccl_second(self):
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				current = Pixel(self.labeled_image.get_pixel(i,j))
				if current.is_not_label(self.background):	
					new_value = self.equiv_table[current.label]	
					self.labeled_image.label_pixel(i, j, new_value)		

	def get_neighbors(self, i, j):
		if i <= 0:
			left = Pixel(self.background)
		else:
			left = Pixel(self.labeled_image.get_pixel(i,j-1))

		if j <= 0:
			upper = Pixel(self.background)
		else:
			upper = Pixel(self.labeled_image.get_pixel(i-1,j))
		
		return (left, upper)

	def label_pixel(self, current, left, upper):
		if left.label == upper.label and left.is_not_label(self.background) and upper.is_not_label(self.background):
			current.label = upper.label
		elif left.label != upper.label and not (left.is_not_label(self.background) and upper.is_not_label(self.background)):
			current.label = max(left.label, upper.label)
		elif left.label != upper.label and left.is_not_label(self.background) and upper.is_not_label(self.background):
		  current.label = min(left.label, upper.label)
		  self.set_equiv_table(left, upper)
		else:
			self.label_counter += 1
			self.equiv_table[self.label_counter] = self.label_counter
			current.label = self.label_counter

	def set_equiv_table(self, left, upper):
		larger = max(left.label, upper.label)
		smaller = min(left.label, upper.label)
		self.equiv_table[larger] = smaller

	def simplify_equiv_table(self):
		for key in self.equiv_table.keys():
			current_key = key
			current_value = self.equiv_table[current_key]
			while current_key > current_value:
				if self.equiv_table[current_value] < current_value:
					current_key = current_value
					current_value = self.equiv_table[current_key]
				else:
					current_key = current_value	
			self.equiv_table[key] = current_value	

		values = list(set(self.equiv_table.values()))
		values.sort()

		new_values = {}
		for idx, val in enumerate(values):
			new_values[val] = idx+1

		for key in self.equiv_table.keys():
			old_value = self.equiv_table[key]
			new_value = new_values[old_value]
			self.equiv_table[key] = new_value

	def print_vals(self):
		# print self.equiv_table.items()
		print self.labeled_image.matrix[50,0:]

	def plot_graph(self):
		plt.imshow(self.labeled_image.matrix)
		plt.show()	
		
class LabeledImage:
	def __init__(self, rows, cols, value):
		self.matrix = value*np.ones((rows,cols), dtype=np.int)

	def get_pixel(self, row, col):
		return self.matrix.item(row,col)

	def label_pixel(self, row, col, label):
		self.matrix.itemset((row,col), label)	


class Pixel:
	def __init__(self, label):
		self.label = label

	def is_label(self, label):
		if self.label == label:
			return True
		else:
			return False

	def is_not_label(self, label):
		if self.label != label:
			return True
		else:
			return False
						
def main():
	img = cv2.imread(sys.argv[1],0)
	bi = BinaryImage(img)
	bi.ccl_first()
	bi.simplify_equiv_table()
	bi.ccl_second()
	# bi.print_vals()
	bi.plot_graph()

if __name__ == "__main__":
	main()	