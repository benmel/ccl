import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt

class BinaryImage:
	def __init__(self, img):
		ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
		self.labeled_image = LabeledImage(thresh)
		self.rows,self.cols = self.labeled_image.shape()
		self.background = 0
		self.label_counter = 0
		self.equiv_table = {}

	def ccl_first(self):
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				current = self.labeled_image.get_pixel(i,j)
				if current.is_not_label(self.background):
					left,upper = self.labeled_image.get_neighbors(i,j)
					self.determine_label(current, left, upper)	
				self.labeled_image.label_pixel(current)

	def ccl_second(self):
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				current = self.labeled_image.get_pixel(i,j)
				if current.is_not_label(self.background):	
					new_pixel = Pixel(self.equiv_table[current.label], i, j)
					self.labeled_image.label_pixel(new_pixel)		

	def determine_label(self, current, left, upper):
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
		print self.equiv_table.items()
		# print self.labeled_image.matrix[50,0:]

	def plot(self):
		self.labeled_image.plot()

	def save(self):
		self.labeled_image.save()	
	

class LabeledImage:
	def __init__(self, matrix):
		self.matrix = matrix

	def shape(self):
		return self.matrix.shape	

	def get_pixel(self, row, col):
		return Pixel(self.matrix.item(row,col), row, col)

	def label_pixel(self, pixel):
		self.matrix.itemset((pixel.row,pixel.col), pixel.label)

	def get_neighbors(self, row, col):
		if row <= 0:
			left = Pixel(self.background)
		else:
			left = self.get_pixel(row,col-1)

		if col <= 0:
			upper = Pixel(self.background)
		else:
			upper = self.get_pixel(row-1,col)
		
		return (left, upper)	

	def plot(self):
		plt.imshow(self.matrix, interpolation = 'nearest')
		plt.xticks([]), plt.yticks([])
		plt.show()

	def save(self):
		plt.imshow(self.matrix, interpolation = 'nearest')
		plt.xticks([]), plt.yticks([])
		plt.savefig('out.png', bbox_inches='tight')		
	

class Pixel:
	def __init__(self, label, row, col):
		self.row = row
		self.col = col
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
	binary_image = BinaryImage(img)
	binary_image.ccl_first()
	binary_image.simplify_equiv_table()
	binary_image.ccl_second()
	binary_image.save()

if __name__ == "__main__":
	main()
		