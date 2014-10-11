import sys
import getopt
import cv2
import numpy as np
from matplotlib import pyplot as plt
from union_find import *

class CCL:
	def __init__(self, img):
		"""Create threshold image"""
		ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
		self.background = 0
		self.labeled_image = LabeledImage(thresh, self.background)
		self.rows,self.cols = self.labeled_image.shape()
		self.label_counter = 0
		"""Union-find structure"""
		self.uf = UnionFind()

	
	def first_pass(self):
		"""First labeling pass"""
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				"""Test if pixel is not background"""
				current = self.labeled_image.get_pixel(i,j)
				if current.is_not_label(self.background):
					"""Get neighbors and then label pixel"""
					left,upper = self.labeled_image.get_neighbors(i,j)
					self.determine_label(current, left, upper)	
					self.labeled_image.label_pixel(current)

	def second_pass(self):
		"""Second labeling pass"""
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				"""Update label using equivalence table"""
				current = self.labeled_image.get_pixel(i,j)
				if current.is_not_label(self.background):	
					current.label = self.find(current)
					self.labeled_image.label_pixel(current)

	def size_filter(self):
		"""Size filter removes noise"""
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				"""Only looks at background pixels"""
				current = self.labeled_image.get_pixel(i,j)
				if current.is_label(self.background):
					"""Test if surrounding pixels are background"""
					surr = self.labeled_image.get_surrounding(i,j)
					other_bg_px = False
					for px in surr:
						if px.is_label(self.background):
							other_bg_px = True
					if not other_bg_px and len(surr) > 0:
						"""Change label if surrounded by non-background pixels"""
						current.label = surr[0].label
						self.labeled_image.label_pixel(current)		

	def determine_label(self, current, left, upper):
		"""Logic to determine label of pixel"""
		if left.label == upper.label and left.is_not_label(self.background) and upper.is_not_label(self.background):
			current.label = upper.label
		elif left.label != upper.label and not (left.is_not_label(self.background) and upper.is_not_label(self.background)):
			current.label = max(left.label, upper.label)
		elif left.label != upper.label and left.is_not_label(self.background) and upper.is_not_label(self.background):
			current.label = min(left.label, upper.label)
			self.union(left, upper)
		else:
			self.label_counter += 1
			current.label = self.label_counter

	def union(self, left, upper):
		"""Add to equivalence table"""
		self.uf.union(left.label, upper.label)

	def find(self, current):
		"""Find in equivalence table"""
		return self.uf[current.label]

	def num_labels(self):
		"""Get number of labels"""
		return len(set(self.uf.parents.values()))				

	def plot(self):
		self.labeled_image.plot()

	def save(self, output_file):
		self.labeled_image.save(output_file)	
	

class LabeledImage:
	def __init__(self, matrix, background):
		"""Store matrix"""
		self.matrix = matrix
		self.background = background

	def shape(self):
		return self.matrix.shape	

	def get_pixel(self, row, col):
		"""Return a specific pixel"""
		return Pixel(self.matrix.item(row,col), row, col)

	def label_pixel(self, pixel):
		"""Label a specific pixel"""
		self.matrix.itemset((pixel.row,pixel.col), pixel.label)

	def get_neighbors(self, row, col):
		"""Return left and upper pixel"""
		if row <= 0:
			left = Pixel(self.background)
		else:
			left = self.get_pixel(row,col-1)
		if col <= 0:
			upper = Pixel(self.background)
		else:
			upper = self.get_pixel(row-1,col)
		return (left, upper)

	def get_surrounding(self, row, col):
		"""Return eight surrounding pixels"""
		locations = [[row+1,col],[row+1,col-1],[row+1,col+1],
								 [row-1,col],[row-1,col-1],[row-1,col+1],
								 [row,col-1],[row,col+1]]
		surr = []
		for loc in locations:
			row_temp = loc[0]
			col_temp = loc[1]
			row_max,col_max = self.shape()
			if row_temp >= 0 and col_temp >= 0 and row_temp < row_max and col_temp < col_max:
				px = self.get_pixel(row_temp,col_temp)
				surr.append(px)
		return surr		

	def plot(self):
		plt.imshow(self.matrix, interpolation = 'nearest')
		plt.xticks([]), plt.yticks([])
		plt.show()

	def save(self, output_file):
		plt.imshow(self.matrix, interpolation = 'nearest')
		plt.xticks([]), plt.yticks([])
		plt.savefig(output_file, bbox_inches='tight')		
	

class Pixel:
	def __init__(self, label, row, col):
		"""Create a pixel with label and coordinates"""
		self.label = label
		self.row = row
		self.col = col

	def is_label(self, label):
		"""Test if pixel has a label"""
		if self.label == label:
			return True
		else:
			return False

	def is_not_label(self, label):
		"""Test if pixel doesn't have a label"""
		if self.label != label:
			return True
		else:
			return False
						
def main():
	def usage():
		print 'python ccl.py [-sf] -i <input_file> [-o <output_file>]'

	input_file = None
	output_file = None
	size_filter = False

	"""Process command line inputs"""
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hsfi:o:", ["help", "size_filter", "input=", "output="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit()
		elif opt in ('-s', '-sf'):
			size_filter = True	
		elif opt in ("-i", "--input"):
			input_file = arg
		elif opt in ("-o", "--output"):
			output_file = arg

	if not input_file:
		usage()
		sys.exit()

	img = cv2.imread(input_file,0)
	ccl = CCL(img)
	if size_filter:
		ccl.size_filter()
	ccl.first_pass()
	ccl.second_pass()
	
	if output_file:
		ccl.save(output_file)
	else:
		ccl.plot()		
	print "Number of labels: " + str(ccl.num_labels())

if __name__ == "__main__":
	main()
		