"""
this file contains code for Tips and tricks for calibrating Machine Learning model like choosing best Regularisation
parameter or checking for underfitting or overfitting.
"""

import numpy as mat
from matplotlib import pyplot
from scipy import io

from MLTricks import Regularised_Linear_Cost_Grad as Rg, learning_curve, Poly_mapping, PlotFit
from MathsTools import FeatureNormalization

mat.set_printoptions(formatter={'float_kind': '{:f}'.format})

# load data
data = io.loadmat("../Data/ex5data1.mat")
# training set
X = data['X']
Y = data['y']

# cross- validation set
Xval = data['Xval']
Yval = data['yval']

# test set
Xtest = data['Xtest']
Ytest = data['ytest']

# plot data
pyplot.xlabel('Change in water level (x)')
pyplot.ylabel('Water flowing out of the dam (y)')
pyplot.plot(X, Y, '+')
print("Plotting data...")
pyplot.show()

# =================================== calculate cost =====================
initial_theta = mat.ones(X.shape[1] + 1)
lamb = 1
# =================================== calculate cost =====================
print("\n=================================== calculate cost =====================")
cost = Rg.cal_cost(initial_theta, mat.c_[mat.ones(X.shape[0]), X], Y, lamb)
print("Cost at theta [1 1] and lambda = 1 should be 303.993192")
print("calculated cost is = ", cost)

# ===================== ============== calculate initial gradient =========================
print("\n=================================== calculate initial gradient =========================")
grad = Rg.cal_grad(initial_theta, mat.c_[mat.ones(X.shape[0]), X], Y, lamb)
print("\ninitial grad should be [-15.303016, 598.250744 ]")
print("Calculated grad are  = ", grad.transpose())

# =============================== Train Linear Regression =============
print("\n=============================== Train Linear Regression =============")
lamb = 0
theta = Rg.optimize_grad(mat.c_[mat.ones(X.shape[0]), X], Y, lamb)
cost = Rg.cal_cost(theta, mat.c_[mat.ones(X.shape[0]), X], Y, lamb)

# =============================== plotting data and line =============================
pred_y = Rg.hypo(mat.c_[mat.ones(X.shape[0]), X], mat.c_[theta])
pyplot.xlabel('Change in water level (x)')
pyplot.ylabel('Water flowing out of the dam (y)')
print("Plotting data...")
pyplot.plot(X, Y, '+', X, pred_y)
pyplot.legend(["Data", "Training Data"])
pyplot.show()

# as we can see that line is not fitting the data this condition is called underfitting or high bias
# as our data is non-linear our line or hyperplane should also be non-linear

# =================================== Learning curve test ==========================
# we are going to draw the variation between cost/error per iteration and apply this technique
# on training and validation set

error_train, error_val, iteration = learning_curve.curve(mat.c_[mat.ones(X.shape[0]), X], Y,
                                                         mat.c_[mat.ones(Xval.shape[0]), Xval], Yval, 0)
pyplot.xlabel('iteration')
pyplot.ylabel('error')
print("Plotting data...")
pyplot.plot(iteration, error_train, iteration, error_val)
pyplot.xlim(0, 13)
pyplot.ylim(0, 150)
pyplot.legend(["training error", "Validation error"])
pyplot.show()

# we can see in the graph the error is increasing with the number of training example increasing and also error is
# high in cross validation set that means adding more example will not going to solve the problem.

# To solve this problem we can add some more features to overcome the under fitting
# we can create new features using polynomial regression.

# we are going to take these existing feature and going to map them in its higher power
# our new feature will look like this --  x1 = (water level), x2 = (water level)^2, xp = (water level)^P

# mapping and normalizing training set
power = 8
X_mapped = Poly_mapping.mapPoly(X, power)

# normalize or scaling the mapped input matrix
X_mapped, mu, sig = FeatureNormalization.normalize(X_mapped)
# adding ones
X_mapped = mat.c_[mat.ones(X_mapped.shape[0]), X_mapped]

# mapping and normalizing test set
X_poly_test = Poly_mapping.mapPoly(Xtest, power)
X_poly_test = mat.subtract(X_poly_test, mu)
X_poly_test = mat.divide(X_poly_test, sig)
X_poly_test = mat.c_[mat.ones(X_poly_test.shape[0]), X_poly_test]  # add ones column

# mapping and normalizing cross validation set
X_poly_val = Poly_mapping.mapPoly(Xval, power)
X_poly_val = mat.subtract(X_poly_val, mu)
X_poly_val = mat.divide(X_poly_val, sig)
X_poly_val = mat.c_[mat.ones(X_poly_val.shape[0]), X_poly_val]  # add ones column

print("\n========================== normalized training examples are ================")
print(X_mapped[0, :])

print("\n================  Training newly added Polynomial Regression set ================ ")
lamb = 0
theta = mat.c_[Rg.optimize_grad(X_mapped, Y, lamb)]

# plotting
min_x = mat.min(X, axis=0)
max_x = mat.max(X, axis=0)
x, x_poly = PlotFit.fit(min_x, max_x, mu, sig, power)

pred_y = Rg.hypo(x_poly, theta)
pyplot.title("Polynomial Regression at lambda = 0")
pyplot.xlabel('Change in water level (x)')
pyplot.ylabel('Water flowing out of the dam (y)')
print("Plotting data...")
pyplot.plot(X, Y, '+', x, pred_y)
pyplot.legend(["Data", "Training Data"])
pyplot.show()

# ================================== Learning Curve for newly added Polynomial Regression ===========
print("\n================  Learning Curve for newly added Polynomial Regression ================ ")

error_train1, error_val1, iteration = learning_curve.curve(X_mapped, Y, X_poly_val, Yval, lamb)

print("Learning curve of poly added feature at lambda =0 ")
pyplot.xlabel('iteration')
pyplot.ylabel('error')
print("Plotting data...")
pyplot.plot(iteration, error_train1, iteration, error_val1)
pyplot.xlim(0, 13)
pyplot.ylim(0, 100)
pyplot.legend(["training error", "Validation error"])
pyplot.show()

# ======================== Choosing best value of Regularization parameter lambda =====================
print("\n===================== Choosing best value of Regularization parameter lambda =======================")

"""
# regularization parameter lambda can effect the model in big way. low value (say 0) can result in overfitting that
means prediction on training set will going to be well but not going to accurate on cross validation or test set. too
high value (say 100) can result in under fitting case in which the it will not going to perform well on any of the
data set so by choosing best lambda value we can make our model more flexible.

# now we are going to calculate weight parameters of training set using multiple regularization parameter (lambda)
value then we are going to calculate cost using all those weight parameter on both training and validation set. the
weight parameter set which going to give the minimum cost/error on validation set that value of lambda is going to
be the best of all
."""

lamb_vec = mat.array([0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10])
cost_train = mat.zeros((len(lamb_vec), 1))
cost_val = mat.zeros((len(lamb_vec), 1))

# calculate parameter set
for i in range(len(lamb_vec)):
    theta = Rg.optimize_grad(X_mapped, Y, lamb_vec[i])
    cost_train[i, :] = Rg.cal_cost(theta, X_mapped, Y, 0)
    cost_val[i, :] = Rg.cal_cost(theta, X_poly_val, Yval, 0)

# find out minimum error on cross validation set
min_val = mat.min(cost_val)  # get the minimum value
ind = mat.where(cost_val == min_val)[0]  # find the minimum value index
print("best value of lambda at validation error = ", min_val, "is = ", lamb_vec[ind])

print("\n================  Learning Curve for errors ================ ")

error_train1, error_val1, iteration = learning_curve.curve(X_mapped, Y, X_poly_val, Yval, lamb)
pyplot.xlabel('lambda')
pyplot.ylabel('error')
print("Plotting data...")
pyplot.plot(lamb_vec, cost_train, lamb_vec, cost_val)
pyplot.legend(["training error", "Validation error"])
pyplot.show()

# =========================== calculating error on test set using best lambda =======================
print("\n======================== calculating error on test set using lambda = ", lamb_vec[ind], "================")

theta = Rg.optimize_grad(X_mapped, Y, lamb_vec[ind])
test_error = Rg.cal_cost(theta, X_poly_test, Ytest, lamb_vec[ind])
print(test_error)
