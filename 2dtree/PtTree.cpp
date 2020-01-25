#include <algorithm>
#include <cmath>
#include <stdexcept>
#include "PtTree.h"

PtTreeNode::PtTreeNode(float& x, float& y, int& index)
{
	this->x = x;
	this->y = y;
	this->index = index;
}

struct less_than_key_x
{
	inline bool operator() (const PtTreeNode* nodeA, const PtTreeNode* nodeB)
	{
		return (nodeA->x < nodeB->x);
	}
};

struct less_than_key_y
{
	inline bool operator() (const PtTreeNode* nodeA, const PtTreeNode* nodeB)
	{
		return (nodeA->y < nodeB->y);
	}
};

PtTreeNode* Next(std::vector<PtTreeNode*> nodes, bool xy)
{
	xy = !xy;
	// xy:		0, 1 == x, y == false, true

	if (xy)
		std::sort(nodes.begin(), nodes.end(), less_than_key_y());
	else
		std::sort(nodes.begin(), nodes.end(), less_than_key_x());

	if (nodes.size() == 0)
		return nullptr;
	
	int index = nodes.size() / 2;
	auto& node = nodes[index];
	node->left = Next(std::vector<PtTreeNode*>(nodes.begin(), nodes.begin() + index), xy);
	node->right = Next(std::vector<PtTreeNode*>(nodes.begin() + index + 1, nodes.end()), xy);
	return node;
}

PtTree::PtTree()
{
}



void PtTree::setPoints(std::vector<Point>& points)
{
	nodes.clear();
	nodes.reserve(points.size());

	for (int i = 0; i < points.size(); i++)
		nodes.push_back(PtTreeNode(points[i].x, points[i].y, i));

	std::vector<PtTreeNode*> nodePtrs;
	nodePtrs.reserve(points.size());

	for (int i = 0; i < nodes.size(); i++)
		nodePtrs.push_back(&(nodes[i]));

	root = Next(nodePtrs, false);
}


inline float getDist2(const Point& target, PtTreeNode* node) {
	float x = target.x - node->x;
	float y = target.y - node->y;
	return x * x + y * y;
}

inline const float& Value(const Point& pt, const bool& xy) {
	if (xy)
		return pt.y;
	return pt.x;
}
inline const float& Value(const PtTreeNode* node, const bool & xy) {
	if (xy)
		return node->y;
	return node->x;
}

void nextNearest(const Point& target, PtTreeNode* current, int& index, float& dist2, bool xy)
{
	float currentDist2 = getDist2(target, current);
	if (currentDist2 <= dist2) {
		dist2 = currentDist2;
		index = current->index;
	}


	xy = !xy;

	bool leftFirst = Value(target, xy) < Value(current, xy);

	// If the target is to the left, execute the left connection first.
	// Only traverse onto the second branch, if the hypersphere intersects the hyperplane.
	if (leftFirst) {
		if (current->left != nullptr)
			nextNearest(target, current->left, index, dist2, xy);

		if (Value(target, xy) + std::sqrt(dist2) > Value(current, xy))
			if (current->right != nullptr)
				nextNearest(target, current->right, index, dist2, xy);
	}
	else {
		if (current->right != nullptr)
			nextNearest(target, current->right, index, dist2, xy);

		if (Value(target, xy) - std::sqrt(dist2) < Value(current, xy))
			if (current->left != nullptr)
				nextNearest(target, current->left, index, dist2, xy);
	}

}

void kNextNearest(const Point& target, PtTreeNode* current, float& maxDist2, int&maxIndex, const int&amount, int* indices, float* distances2, bool xy) {
	float currentDist2 = getDist2(target, current);

	if (currentDist2 < maxDist2) {
		// Replace the maximum.
		indices[maxIndex] = current->index;
		distances2[maxIndex] = currentDist2;

		// Update the maximum distance.
		maxIndex = 0;
		float newMaxDist2 = distances2[0];
		for (int i = 1; i < amount; i++)
		{
			if (distances2[i] > distances2[maxIndex]) {
				maxIndex = i;
				newMaxDist2 = distances2[i];
			}
		}
		maxDist2 = newMaxDist2;
	}


	xy = !xy;

	bool leftFirst = Value(target, xy) < Value(current, xy);

	if (leftFirst) {
		if (current->left != nullptr)
			kNextNearest(target, current->left, maxDist2, maxIndex, amount, indices, distances2, xy);

		if (Value(target, xy) + std::sqrt(maxDist2) > Value(current, xy))
			if (current->right != nullptr)
				kNextNearest(target, current->right, maxDist2, maxIndex, amount, indices, distances2, xy);
	}
	else {
		if (current->right != nullptr)
			kNextNearest(target, current->right, maxDist2, maxIndex, amount, indices, distances2, xy);

		if (Value(target, xy) - std::sqrt(maxDist2) < Value(current, xy))
			if (current->left != nullptr)
				kNextNearest(target, current->left, maxDist2, maxIndex, amount, indices, distances2, xy);
	}
}




int PtTree::nearest(const Point& target, float& maxDist2)
{
	if (root == nullptr) {
		throw std::logic_error("The PtTree must be populated before a lookup.");
	}

	int index = -1;
	nextNearest(target, root, index, maxDist2, false);

	return index;
}


void PtTree::kNearest(const Point& target, float& maxDist2, int* indices, float * distances2, const int& amount)
{
	if (root == nullptr) {
		throw std::logic_error("The PtTree must be populated before a lookup.");
	}
	
	for (int i = 0; i < amount; i++) {
		distances2[i] = maxDist2;
		indices[i] = -1;
	}

	int maxIndex = 0;
	kNextNearest(target, root, maxDist2, maxIndex, amount, indices, distances2, false);
}
