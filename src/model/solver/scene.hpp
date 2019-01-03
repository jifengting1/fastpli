#ifndef SCENE_HPP_
#define SCENE_HPP_

#include <vector>

#include "fiber_class.hpp"
#include "include/vemath.hpp"

#include <GL/gl.h>
#include <GL/glut.h>

class Scene {
 public:
   Scene(int argc, char **argv);
   ~Scene();

   void SetViewAngle(const float x, const float y, const float z);
   void DrawScene(const std::vector<object::Fiber> &fibers);
   void SavePPM(const char *fname, int start_x = 0, int start_y = 0);

 private:
   void AutoVolume(const std::vector<object::Fiber> &fibers);
   void CheckWindowSize();

   GLUquadricObj *quadObj_;
   vm::Vec3<float> rotation_ = 0;

   vm::Vec3<float> volume_dim_ = 10000;
   vm::Vec3<float> offset_ = {0, 0, -300};
};

#endif // SCENECLASS_HPP_