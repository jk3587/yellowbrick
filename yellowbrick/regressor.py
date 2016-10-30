# yellowbrick.regressor
# Visualizations related to evaluating Scikit-Learn regressor models
#
# Author:   Rebecca Bilbro <rbilbro@districtdatalabs.com>
# Author:   Benjamin Bengfort <bbengfort@districtdatalabs.com>
# Created:  Fri Jun 03 10:30:36 2016 -0700
#
# Copyright (C) 2016 District Data Labs
# For license information, see LICENSE.txt
#
# ID: regressor.py [4a59c49] benjamin@bengfort.com $

"""
Visualizations related to evaluating Scikit-Learn regressor models
"""

##########################################################################
## Imports
##########################################################################

import matplotlib as mpl
import matplotlib.pyplot as plt

from .bestfit import draw_best_fit
from .exceptions import YellowbrickTypeError
from .utils import get_model_name, isestimator, isregressor
from .base import Visualizer, ScoreVisualizer, MultiModelMixin

##########################################################################
## Regression Visualization Base Object
##########################################################################

class RegressionScoreVisualizer(ScoreVisualizer):
    def __init__(self, model, **kwargs):
        """
        Check to see if model is an instance of a regressor.
        Should return an error if it isn't.
        """
        if not isregressor(model):
            raise YellowbrickTypeError(
                "This estimator is not a regressor; try a classifier or "
                "clustering score visualizer instead!"
        )

        super(RegressionScoreVisualizer, self).__init__(model, **kwargs)


##########################################################################
## Prediction Error Plots
##########################################################################

class PredictionError(RegressionScoreVisualizer):
    """
    Plot the actual targets from the dataset against the
    predicted values generated by our model(s).
    """
    def __init__(self, model, **kwargs):
        """
        Parameters
        ----------

        :param ax: the axis to plot the figure on.

        :param estimator: the Scikit-Learn estimator
            Should be an instance of a regressor, else the __init__ will
            return an error.

        :param kwargs: keyword arguments passed to the super class.
            Currently passing in hard-coded colors for the prediction error
            points and the line of best fit.
            These will be refactored to a default Yellowbrick style.


        These parameters can be influenced later on in the visualization
        process, but can and should be set as early as possible.
        """

        super(PredictionError, self).__init__(model, **kwargs)

        ## hoisted to Visualizer base class
        # self.ax = None

        ## hoisted to ScoreVisualizer
        # self.name = get_model_name(self.estimator)

        self.colors = {
            'point': kwargs.pop('point_color', '#F2BE2C'),
            'line': kwargs.pop('line_color', '#2B94E9'),
        }
        # self.fig, self.ax = plt.subplots()

    def score(self, X, y=None, **kwargs):
        """
        Originally score  for prediction error was conceived as generating
        y_pred by calling the sklearn function cross_val_predict on the
        model, X, y, and the specified number of folds, e.g.:

            y_pred = cv.cross_val_predict(model, X, y, cv=12)

        With the new API, there's not much for score to do.

        Parameters
        ----------
        X : array-like
            X (also X_test) are the dependent variables of test set to predict

        y : array-like
            y (also y_test) is the independent actual variables to score against

        Returns
        ------

        ax : the axis with the plotted figure

        """
        y_pred = self.predict(X)
        return self.draw(y, y_pred)

    def draw(self, y, y_pred):
        """
        Parameters
        ----------

        y : ndarray or Series of length n
            An array or series of target or class values

        y_pred : ndarray or Series of length n
            An array or series of predicted target values

        Returns
        ------

        ax : the axis with the plotted figure
        """
        if self.ax is None:
            self.ax = plt.gca()

        self.ax.scatter(y, y_pred, c='#F2BE2C')

        # TODO If score is happening inside a loop, draw would get called multiple times.
        # Ideally we'd want the best fit line to be drawn only once
        draw_best_fit(y, y_pred, self.ax, 'linear', ls='--', lw=2, c=self.colors['line'])

        self.ax.set_xlim(y.min()-1, y.max()+1)
        self.ax.set_ylim(y_pred.min()-1, y_pred.max()+1)

        return self.ax

    def poof(self):
        """
        Returns
        ------

        ax : the axis with the plotted, labelled and formatted figure

        """
        self.ax.set_title('Prediction Error for {}'.format(self.name))
        self.ax.set_ylabel('Predicted')
        plt.xlabel('Measured')
        plt.show()

        return self.ax

##########################################################################
## Residuals Plots
##########################################################################

class ResidualsPlot(RegressionScoreVisualizer):
    """
    A residual plot shows the residuals on the vertical axis
    and the independent variable on the horizontal axis.

    If the points are randomly dispersed around the horizontal axis,
    a linear regression model is appropriate for the data;
    otherwise, a non-linear model is more appropriate.
    """
    def __init__(self, model, **kwargs):
        """
        Parameters
        ----------

        :param ax: the axis to plot the figure on.

        :param estimator: the Scikit-Learn estimator
            Should be an instance of a regressor, else the __init__ will
            return an error.

        :param kwargs: keyword arguments passed to the super class.
            Currently passing in hard-coded colors for the residual train and
            test points and the horizontal line.
            These will be refactored to a default Yellowbrick style.

        These parameters can be influenced later on in the visualization
        process, but can and should be set as early as possible.

        """

        super(ResidualsPlot, self).__init__(model, **kwargs)

        ## hoisted to Visualizer base class
        # self.ax = None

        ## hoisted to ScoreVisualizer
        # self.name = get_model_name(self.estimator)

        # TODO Is there a better way to differentiate between train and test points?
        # We'd like to color them differently in draw...
        # Can the user pass those in as keyword arguments?
        self.colors = {
            'train_point': kwargs.pop('train_point_color', '#2B94E9'),
            'test_point': kwargs.pop('test_point_color', '#94BA65'),
            'line': kwargs.pop('line_color', '#333333'),
        }


    def fit(self, X, y=None, **kwargs):
        """
        Parameters
        ----------

        X : ndarray or DataFrame of shape n x m
            A matrix of n instances with m features

        y : ndarray or Series of length n
            An array or series of target values

        kwargs: keyword arguments passed to Scikit-Learn API.
        """
        super(ResidualsPlot, self).fit(X, y, **kwargs)
        self.score(X, y, train=True)

    def score(self, X, y=None, train=False, **kwargs):
        """
        Generates predicted target values using the Scikit-Learn
        estimator.

        Parameters
        ----------
        X : array-like
            X (also X_test) are the dependent variables of test set to predict

        y : array-like
            y (also y_test) is the independent actual variables to score against

        train : boolean
            If False, `score` assumes that the residual points being plotted
            are from the test data; if True, `score` assumes the residuals
            are the train data.

        Returns
        ------

        ax : the axis with the plotted figure

        """
        y_pred = self.predict(X)
        scores = y_pred - y
        self.draw(y_pred, scores, train=train)

    def draw(self, y_pred, residuals, train=False, **kwargs):
        """
        Parameters
        ----------
        y_pred : ndarray or Series of length n
            An array or series of predicted target values

        residuals : ndarray or Series of length n
            An array or series of the difference between the predicted and the
            target values

        train : boolean
            If False, `draw` assumes that the residual points being plotted
            are from the test data; if True, `draw` assumes the residuals
            are the train data.

        Returns
        ------

        ax : the axis with the plotted figure

        """
        if self.ax is None:
            self.ax = plt.gca()

        color = self.colors['train_point'] if train else self.colors['test_point']
        alpha = 0.5 if train else 1.0

        self.ax.scatter(y_pred, residuals, c=color, s=40, alpha=alpha)

        return self.ax

    def poof(self):
        """

        Returns
        ------

        ax : the axis with the plotted, labelled and formatted figure

        """
        if self.ax is None: return

        self.ax.hlines(y=0, xmin=0, xmax=100)
        self.ax.set_title('Residuals for {} Model'.format(self.name))
        self.ax.set_ylabel('Residuals')
        plt.xlabel("Predicted Value")

        plt.show()

        return self.ax
