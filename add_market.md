How to add a Market API
===================

One of MExBtcAPI's purposes is to support operations on multiple markets with similar semantics. If you find that your favorite market is not supported, you may want to develop a market API for it and integrate it with MExBtcAPI. This document will guide you in the process.


Steps
====

 - Locate the market API documentation in the market website. If there's none, it will be difficult (or downright impossible) to support it correctly.
 - Write a python module that exposes the market API. Here are some guidelines:
  - Each API call should be exposed in a single python function
  - The return of each function should be native python datatypes (int, string, etc).
  - If you're dealing with decimal (non-integer) numbers, you should NOT use float. Use string or Decimal instead (reasoning is provided below).
 - Write a separate (wrapper) module that uses your market API module and implements the MExBtcAPI interfaces
  - You should familiarize yourself with the classes in the mexbtcapi/concepts directory first
  - If there's data or functionality that is exposed by MExBtcAPI but your market doesn't provide, a revision of the interfaces is probably in order - you should file a bug request for that.

Why should I write two modules instead of only one?
=========================================

If you write two modules:

 - The market API can be used independently of MExBtcAPI
 - The interface and implementation are separated


Why shouldn't I use float?
====================

Put shortly, since some finite decimal (base 10\. numbers don't have a finite binary representation, floats introduce rounding errors that you really want to avoid when doing accounting, and dealing with money, in general.
A more detailed explanation can be found [on StackOverflow](http://stackoverflow.com/questions/61872/use-float-or-decimal-for-accounting-application-dollar-amount).

# Anything else I should know?
Probably. If you have any questions or feel like something is missing here, don't hesitate to contact the maintainer or file a bug
