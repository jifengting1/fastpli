#ifndef OCT_TREE_HPP_
#define OCT_TREE_HPP_

#include <array>
#include <set>
#include <tuple>
#include <vector>

#include "cone_class.hpp"
#include "fiber_class.hpp"
#include "include/aabb.hpp"
#include "include/vemath.hpp"

class OctTree {
 public:
   OctTree(const std::vector<geometry::Fiber> &fibers,
           const double min_cube_size, const aabb::AABB<double, 3> col_voi);
   std::set<std::array<size_t, 4>> Run();

   int max_level() { return max_level_; };

 private:
   std::tuple<std::vector<std::vector<size_t>>, int>
   GenerateLeafs(const std::vector<size_t> &ids,
                 const aabb::AABB<double, 3> &cube, int level);
   std::set<std::array<size_t, 4>>
   TestCollision(const std::vector<size_t> &cone_ids);

   std::vector<object::Cone> cones_;
   int max_level_ = 0;
   double min_cube_size_ = 0;
   aabb::AABB<double, 3> main_cube_;
   const size_t kMaxParticle_ = 10;
   const int kMaxThreadLevel_ = 1;
};

#endif // OCT_TREE_HPP_
