#ifndef PTTREE_H
#define PTTREE_H

#include <vector>

class Point {
public:
	float x, y;
	Point() { };
	Point(const float& x, const float& y) {
		this->x = x;
		this->y = y;
	};
};

class PtTreeNode {
public:
	float x, y;
	int index;
	PtTreeNode* left = nullptr;
	PtTreeNode* right = nullptr;

	PtTreeNode(float& x, float& y, int& index);
};

class PtTree {
private:
	std::vector<PtTreeNode> nodes;

	PtTreeNode* root = nullptr;

public:
	PtTree();
	void setPoints(std::vector<Point>& points);
	int nearest(const Point& target, float& maxDist2);

	void kNearest(const Point& target, float& maxDist2, int* indices, float * distances2, const int& amount);
};

#endif