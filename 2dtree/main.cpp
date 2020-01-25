#include <iostream>
#include <string>
#include <algorithm>
#include <iterator>
#include <memory>
#include "PtTree.h"

int main(int argc, char* argv[])
{
	if (argc > 1) goto main;
	else goto help;
invalid:
	std::cout << "\nInvalid input.";
help:
	std::cout << "\nSupply arguments:\n\n"
		<< "> amount        ... (Integer) amount of points to search for\n"
		<< "> radius        ... (radius) radius to search in\n"
		<< "> point         ... (Point) query point\n"
		<< "> points[]      ... (Points) points to populate the tree with\n"
		<< "\n\n Note, a point must be given as 'xx.xxx,y.y' with no spaces.";
	return 0;
main:

	std::vector<Point> points;
	if (argc < 5) goto invalid;

	for (int i = 3; i < argc; ++i) {
		std::string str = argv[i];
		size_t comma = str.find(',');

		if (comma == std::string::npos) goto invalid;
		
		float x = std::atof(str.substr(0, comma).c_str()),
		      y = std::atof(str.substr(comma + 1).c_str());


		points.push_back(Point(x, y));
	}

	// Query input.
	Point query = points[0];
	int amount = std::atoi(argv[1]);
	float radius = std::atof(argv[2]),
		  radius2 = radius * radius;

	// Build tree.
	points.erase(points.begin());
	PtTree tree;
	tree.setPoints(points);
	
	// Make query and print results.
	
	if (amount < 1) goto invalid;
	if (amount == 1) {
		int result = tree.nearest(query, radius2);
		std::cout << result << " " << radius2;
	}
	else {
		float *distances2 = new float[amount];
		int *indices = new int[amount];
		tree.kNearest(query, radius2, indices, distances2, amount);
		for (int i = 0; i < amount; i++)
		{
			std::cout << indices[i] << " " << distances2[i];
			if (i != amount - 1 ) std::cout << "\n";
		}
		delete[] distances2;
		delete[] indices;
	}

	return 1;

}