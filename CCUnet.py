import tensorflow as tf
import os
import glob
import cv2
import numpy as np
import random
import math
import sys
from scipy.io import loadmat

# get model name and training fold
model_name = sys.argv[0][:-3]
train_fold = sys.argv[1]

# default parameters
EPS = 1e-12
BOARD_FILL_COLOR = 1e-5
best_record = 10
learning_rate = 2*1e-4
epochs = 10000

# dataset path
train_picture_path = './datasets/ColorChecker_Recommended/'

# the file path to save images during training
train_save_path = model_name + '_' + train_fold + '_train/'
if not os.path.exists(train_save_path):
	os.makedirs(train_save_path)

# the file path to save model during training
model_save_path = model_name + '_' + train_fold + '_model/'
if not os.path.exists(model_save_path):
	os.makedirs(model_save_path)

# the file path to save images during testing
test_save_path = model_name + '_' + train_fold + '_test/'
if not os.path.exists(test_save_path):
	os.makedirs(test_save_path)

# folds information recommended by Gehler, which is the author of the ColorChecher dataset
# It is evenly divided according to the distribution of the illuminant information
tr_fold1=[2, 4, 6, 7, 8, 9, 10, 13, 14, 15, 17, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 58, 61, 62, 64, 65, 67, 69, 76, 77, 80, 81, 82, 84, 85, 86, 87, 89, 91, 92, 93, 94, 95, 96, 98, 99, 100, 102, 104, 105, 106, 107, 108, 110, 111, 112, 115, 118, 119, 120, 121, 126, 128, 129, 131, 133, 135, 137, 138, 139, 140, 142, 143, 145, 147, 149, 150, 151, 153, 154, 157, 158, 160, 168, 170, 171, 174, 175, 176, 177, 178, 183, 184, 185, 186, 188, 189, 191, 192, 193, 194, 196, 197, 198, 199, 200, 201, 202, 204, 205, 206, 209, 211, 212, 213, 215, 216, 217, 220, 222, 223, 225, 226, 227, 228, 229, 230, 231, 232, 233, 235, 236, 237, 239, 241, 243, 244, 245, 246, 247, 248, 249, 251, 252, 253, 254, 256, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 269, 271, 272, 273, 274, 275, 277, 278, 280, 281, 282, 284, 285, 287, 289, 291, 292, 294, 295, 296, 297, 298, 300, 301, 302, 303, 305, 306, 307, 309, 311, 312, 313, 314, 315, 316, 317, 318, 320, 321, 323, 325, 326, 327, 329, 334, 335, 336, 337, 339, 342, 343, 344, 345, 346, 348, 349, 350, 351, 352, 353, 355, 356, 360, 361, 362, 365, 367, 368, 369, 371, 372, 373, 375, 376, 377, 378, 379, 380, 381, 382, 385, 387, 388, 391, 392, 393, 396, 397, 399, 401, 403, 404, 406, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 421, 422, 424, 432, 435, 436, 437, 438, 439, 440, 441, 443, 444, 446, 448, 449, 451, 452, 453, 454, 457, 458, 459, 460, 461, 462, 464, 465, 466, 467, 468, 469, 471, 472, 473, 475, 476, 477, 478, 479, 481, 483, 484, 485, 486, 487, 488, 489, 492, 493, 496, 498, 500, 501, 503, 505, 506, 510, 511, 512, 514, 516, 517, 518, 519, 520, 522, 523, 524, 528, 529, 531, 532, 534, 535, 536, 537, 538, 540, 541, 543, 544, 545, 546, 547, 548, 549, 550, 551, 555, 556, 557, 558, 560, 561, 562, 565, 566, 567]
tr_fold2=[1, 3, 5, 6, 7, 8, 9, 11, 12, 15, 16, 18, 19, 20, 22, 23, 26, 27, 29, 32, 33, 36, 37, 39, 41, 43, 45, 48, 50, 54, 55, 56, 57, 59, 60, 62, 63, 65, 66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 81, 82, 83, 88, 89, 90, 91, 93, 95, 96, 97, 99, 101, 103, 104, 108, 109, 110, 111, 112, 113, 114, 116, 117, 118, 122, 123, 124, 125, 127, 128, 129, 130, 131, 132, 133, 134, 136, 137, 140, 141, 143, 144, 146, 147, 148, 152, 154, 155, 156, 157, 159, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 172, 173, 174, 175, 178, 179, 180, 181, 182, 183, 184, 185, 187, 188, 189, 190, 192, 193, 194, 195, 196, 198, 199, 203, 204, 207, 208, 210, 211, 212, 214, 215, 216, 217, 218, 219, 221, 222, 223, 224, 225, 226, 229, 230, 232, 234, 238, 239, 240, 241, 242, 244, 245, 248, 249, 250, 252, 253, 255, 257, 260, 261, 263, 265, 266, 267, 268, 270, 271, 272, 273, 276, 277, 279, 280, 281, 282, 283, 286, 288, 289, 290, 291, 292, 293, 295, 296, 299, 301, 302, 303, 304, 308, 309, 310, 312, 313, 316, 318, 319, 321, 322, 324, 328, 330, 331, 332, 333, 334, 335, 336, 337, 338, 340, 341, 343, 344, 347, 349, 350, 352, 353, 354, 357, 358, 359, 360, 362, 363, 364, 366, 367, 368, 370, 371, 372, 373, 374, 377, 378, 379, 380, 383, 384, 385, 386, 388, 389, 390, 392, 394, 395, 398, 400, 402, 404, 405, 407, 408, 409, 417, 418, 420, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 433, 434, 436, 437, 439, 442, 445, 446, 447, 449, 450, 452, 453, 454, 455, 456, 457, 461, 463, 466, 468, 469, 470, 473, 474, 476, 478, 479, 480, 482, 483, 484, 487, 488, 489, 490, 491, 494, 495, 496, 497, 498, 499, 502, 504, 507, 508, 509, 510, 511, 513, 514, 515, 517, 520, 521, 522, 523, 525, 526, 527, 528, 529, 530, 531, 532, 533, 535, 537, 538, 539, 542, 543, 546, 547, 548, 551, 552, 553, 554, 556, 557, 559, 560, 561, 562, 563, 564, 565, 567, 568]
tr_fold3=[1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 28, 30, 31, 33, 34, 35, 38, 40, 41, 42, 44, 45, 46, 47, 48, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 63, 64, 66, 68, 69, 70, 71, 72, 73, 74, 75, 78, 79, 80, 83, 84, 85, 86, 87, 88, 90, 92, 94, 97, 98, 100, 101, 102, 103, 105, 106, 107, 109, 113, 114, 115, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126, 127, 130, 132, 134, 135, 136, 138, 139, 141, 142, 144, 145, 146, 148, 149, 150, 151, 152, 153, 155, 156, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 169, 171, 172, 173, 176, 177, 179, 180, 181, 182, 186, 187, 190, 191, 195, 197, 200, 201, 202, 203, 205, 206, 207, 208, 209, 210, 213, 214, 218, 219, 220, 221, 224, 227, 228, 231, 233, 234, 235, 236, 237, 238, 240, 242, 243, 246, 247, 250, 251, 254, 255, 256, 257, 258, 259, 262, 264, 268, 269, 270, 274, 275, 276, 278, 279, 283, 284, 285, 286, 287, 288, 290, 293, 294, 297, 298, 299, 300, 304, 305, 306, 307, 308, 310, 311, 314, 315, 317, 319, 320, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 338, 339, 340, 341, 342, 345, 346, 347, 348, 351, 354, 355, 356, 357, 358, 359, 361, 363, 364, 365, 366, 369, 370, 374, 375, 376, 381, 382, 383, 384, 386, 387, 389, 390, 391, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 419, 420, 421, 423, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 438, 440, 441, 442, 443, 444, 445, 447, 448, 450, 451, 455, 456, 458, 459, 460, 462, 463, 464, 465, 467, 470, 471, 472, 474, 475, 477, 480, 481, 482, 485, 486, 490, 491, 492, 493, 494, 495, 497, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 512, 513, 515, 516, 518, 519, 521, 524, 525, 526, 527, 530, 533, 534, 536, 539, 540, 541, 542, 544, 545, 549, 550, 552, 553, 554, 555, 558, 559, 563, 564, 566, 568]

te_fold1=[431, 497, 304, 155, 515, 219, 234, 113, 144, 181, 172, 124, 494, 33, 179, 507, 508, 426, 447, 187, 445, 257, 499, 156, 427, 169, 433, 530, 18, 490, 308, 167, 161, 504, 286, 90, 218, 425, 48, 132, 134, 208, 434, 276, 165, 509, 474, 428, 148, 455, 182, 463, 279, 255, 502, 495, 117, 159, 127, 407, 270, 163, 456, 162, 203, 288, 116, 130, 290, 283, 190, 224, 221, 430, 180, 207, 97, 429, 310, 299, 109, 101, 442, 164, 173, 408, 88, 470, 166, 125, 141, 114, 480, 103, 152, 210, 136, 238, 250, 409, 482, 268, 491, 57, 293, 19, 450, 341, 72, 70, 5, 214, 364, 402, 370, 195, 319, 328, 374, 384, 542, 568, 420, 123, 68, 16, 56, 564, 539, 526, 400, 357, 12, 1, 553, 552, 45, 383, 63, 354, 398, 79, 54, 74, 3, 358, 395, 333, 22, 525, 146, 78, 338, 322, 389, 324, 340, 73, 390, 359, 240, 71, 83, 423, 242, 533, 405, 521, 41, 331, 332, 66, 527, 563, 363, 59, 55, 122, 75, 554, 11, 394, 330, 513, 366, 386, 347, 559, 60]
te_fold2=[412, 413, 94, 171, 419, 160, 258, 287, 105, 264, 477, 465, 443, 485, 35, 200, 516, 448, 307, 306, 235, 142, 278, 126, 464, 481, 269, 300, 493, 201, 209, 262, 38, 139, 444, 106, 294, 501, 34, 138, 459, 205, 414, 441, 471, 519, 237, 462, 432, 191, 176, 410, 231, 100, 98, 440, 472, 274, 220, 202, 411, 475, 438, 503, 298, 233, 186, 150, 135, 120, 492, 251, 458, 228, 275, 506, 297, 460, 451, 518, 87, 102, 467, 153, 119, 17, 435, 236, 92, 206, 158, 256, 415, 121, 115, 285, 259, 149, 254, 213, 500, 505, 284, 305, 151, 177, 486, 107, 47, 558, 342, 549, 247, 540, 325, 315, 323, 391, 356, 339, 53, 40, 243, 381, 397, 85, 52, 393, 369, 69, 396, 49, 246, 51, 536, 326, 44, 61, 58, 197, 361, 399, 145, 346, 25, 317, 46, 406, 375, 28, 550, 84, 64, 421, 348, 355, 10, 512, 13, 541, 21, 2, 86, 555, 545, 365, 320, 30, 345, 327, 227, 329, 31, 544, 4, 416, 403, 534, 351, 42, 382, 376, 566, 14, 24, 314, 387, 80, 524, 311, 401]
te_fold3=[476, 295, 468, 489, 118, 77, 301, 128, 193, 289, 469, 183, 303, 184, 418, 232, 91, 131, 479, 484, 174, 111, 204, 95, 104, 263, 281, 483, 212, 488, 271, 211, 175, 189, 225, 137, 261, 154, 37, 309, 452, 461, 292, 449, 248, 424, 517, 93, 496, 296, 96, 478, 133, 110, 194, 249, 129, 436, 498, 520, 267, 252, 140, 185, 282, 272, 229, 168, 302, 453, 446, 178, 39, 226, 291, 457, 280, 277, 537, 273, 76, 188, 62, 170, 454, 253, 260, 89, 239, 222, 230, 487, 417, 112, 143, 466, 265, 108, 147, 437, 157, 99, 223, 192, 266, 439, 36, 523, 344, 562, 422, 217, 353, 379, 27, 20, 371, 360, 215, 32, 377, 362, 343, 531, 216, 65, 557, 321, 378, 532, 543, 380, 337, 514, 352, 551, 349, 350, 199, 15, 6, 241, 67, 548, 404, 535, 336, 546, 50, 473, 372, 565, 29, 511, 7, 560, 316, 245, 528, 547, 43, 244, 81, 318, 368, 313, 312, 529, 561, 8, 392, 335, 23, 82, 26, 367, 567, 196, 334, 522, 198, 388, 510, 373, 556, 385, 9, 538]

# the coordinates of MacBeth colorchecker in each image 
coordinates = [[801, 1277, 1312, 1986], [180, 1061, 872, 1984], [896, 843, 1202, 1315], [832, 1221, 1021, 1490], [474, 1153, 726, 1448], [455, 828, 715, 1106], [500, 1355, 971, 1703], [1023, 1034, 1207, 1296], [457, 1131, 618, 1353], [162, 315, 937, 764], [544, 234, 1220, 705], [95, 1113, 1173, 1979], [329, 1073, 1304, 1815], [737, 204, 1255, 860], [1018, 337, 1297, 745], [765, 328, 970, 497], [911, 1168, 1100, 1413], [717, 1619, 872, 1841], [796, 1145, 1194, 1723], [400, 342, 560, 715], [735, 226, 1357, 1076], [673, 211, 1316, 1087], [734, 1502, 1198, 1892], [254, 59, 1086, 675], [877, 589, 1357, 1299], [649, 1410, 1049, 1912], [378, 1285, 763, 1864], [828, 1364, 1264, 1994], [717, 353, 1105, 911], [321, 153, 1078, 711], [874, 853, 1340, 1579], [357, 190, 1141, 755], [943, 377, 1107, 503], [1026, 1194, 1123, 1333], [136, 1687, 381, 1906], [1024, 1491, 1134, 1658], [1040, 1548, 1239, 1776], [486, 1646, 591, 1802], [952, 776, 1236, 978], [905, 301, 1102, 563], [854, 251, 1231, 611], [423, 1503, 755, 1924], [538, 1468, 735, 1746], [902, 1433, 1212, 1657], [1076, 1318, 1221, 1660], [719, 122, 1203, 537], [859, 1260, 1250, 1997], [809, 1489, 1093, 1867], [844, 1424, 1094, 1826], [700, 1196, 1127, 1880], [314, 564, 458, 708], [721, 859, 1064, 1097], [724, 1075, 1010, 1257], [674, 892, 873, 1160], [706, 1267, 888, 1511], [866, 1025, 1325, 1588], [666, 781, 994, 1053], [885, 1105, 1146, 1488], [175, 876, 351, 1122], [760, 1170, 887, 1331], [625, 1259, 772, 1435], [192, 521, 806, 1049], [264, 276, 760, 889], [185, 1455, 489, 1676], [324, 295, 563, 544], [655, 384, 836, 509], [892, 1343, 1202, 1833], [707, 1454, 983, 1841], [967, 591, 1329, 1052], [389, 287, 710, 752], [396, 429, 937, 833], [918, 831, 1203, 1289], [780, 1214, 1132, 1696], [880, 492, 1151, 880], [1063, 410, 1229, 636], [892, 1603, 1108, 1889], [704, 296, 1035, 537], [758, 215, 1046, 594], [406, 696, 605, 845], [479, 223, 910, 970], [293, 620, 623, 1072], [567, 268, 769, 415], [772, 409, 957, 761], [280, 1101, 537, 1309], [459, 522, 606, 734], [365, 202, 1022, 669], [678, 1636, 716, 1701], [643, 694, 679, 757], [666, 1739, 718, 1832], [699, 1690, 863, 1930], [804, 1810, 885, 1940], [814, 1655, 882, 1771], [1110, 769, 1260, 864], [1217, 1069, 1378, 1182], [833, 1765, 895, 1886], [244, 558, 348, 631], [879, 1679, 1018, 1880], [164, 1099, 334, 1226], [692, 288, 768, 411], [516, 188, 716, 457], [796, 1869, 869, 1993], [356, 1417, 619, 1798], [487, 287, 674, 550], [934, 1786, 1055, 1996], [954, 1867, 1038, 2013], [360, 311, 540, 588], [185, 1321, 289, 1392], [987, 1667, 1303, 1876], [727, 1592, 1067, 2059], [557, 1565, 978, 2192], [872, 1837, 1012, 2081], [67, 1529, 800, 2175], [458, 9, 1319, 739], [1010, 1977, 1070, 2075], [337, 98, 724, 563], [1104, 1871, 1177, 1993], [150, 1189, 454, 1386], [865, 1886, 956, 2022], [952, 1715, 1249, 2131], [1177, 1813, 1324, 2020], [780, 365, 1272, 984], [588, 1939, 722, 2160], [786, 1599, 1125, 2074], [1021, 1725, 1181, 1952], [865, 1676, 1109, 2024], [1022, 1915, 1180, 2149], [883, 131, 1141, 557], [730, 1645, 1027, 2070], [381, 1735, 588, 2037], [719, 1645, 792, 1769], [684, 1694, 759, 1816], [118, 162, 507, 643], [241, 1266, 387, 1357], [476, 1687, 664, 1966], [531, 1669, 912, 2135], [575, 1828, 741, 2154], [650, 1724, 953, 2072], [308, 1551, 722, 2114], [989, 1804, 1297, 2175], [255, 1426, 349, 1478], [568, 1569, 955, 2104], [843, 236, 919, 360], [302, 98, 805, 710], [454, 1250, 1161, 2167], [470, 1395, 668, 1758], [398, 1060, 1176, 2190], [846, 1524, 975, 1710], [575, 1722, 738, 1964], [403, 1636, 751, 2110], [390, 292, 696, 652], [1007, 1925, 1075, 2047], [607, 348, 691, 476], [962, 300, 1100, 492], [815, 315, 937, 472], [882, 1659, 1082, 1930], [989, 314, 1172, 582], [599, 66, 1270, 835], [550, 279, 638, 412], [759, 479, 965, 720], [541, 245, 638, 386], [833, 789, 889, 880], [1046, 368, 1204, 586], [904, 413, 1041, 610], [655, 322, 870, 595], [741, 187, 982, 522], [385, 116, 721, 572], [273, 451, 543, 655], [767, 535, 836, 649], [236, 1242, 323, 1295], [1075, 1010, 1234, 1115], [664, 291, 750, 444], [743, 275, 842, 453], [148, 985, 522, 1288], [942, 454, 1139, 722], [1124, 522, 1289, 748], [660, 405, 743, 543], [784, 1762, 907, 1960], [28, 117, 786, 793], [624, 186, 892, 577], [761, 1675, 987, 2048], [999, 1826, 1188, 2092], [123, 335, 438, 585], [958, 1683, 1161, 1983], [1062, 1670, 1308, 2012], [610, 191, 725, 388], [874, 233, 1193, 625], [721, 442, 769, 526], [635, 1803, 796, 2081], [790, 1722, 846, 1817], [85, 970, 304, 1114], [67, 995, 305, 1150], [864, 540, 1080, 842], [985, 363, 1258, 590], [935, 821, 1078, 1021], [1076, 435, 1266, 695], [542, 1805, 795, 2099], [695, 1591, 1059, 2076], [228, 840, 446, 1001], [879, 279, 1134, 564], [621, 1495, 756, 1709], [962, 263, 1092, 464], [121, 838, 367, 1012], [739, 1836, 835, 2000], [738, 418, 855, 575], [794, 1777, 920, 1966], [732, 1839, 823, 1988], [877, 284, 1086, 578], [863, 1564, 1365, 2154], [79, 54, 765, 711], [915, 1514, 1295, 2016], [770, 1503, 1315, 2070], [149, 962, 363, 1108], [1007, 593, 1299, 801], [861, 235, 1156, 605], [678, 1674, 999, 2091], [878, 1775, 1029, 1993], [943, 1729, 1198, 2035], [1166, 791, 1402, 1078], [1204, 911, 1381, 1120], [988, 1583, 1139, 1826], [602, 558, 904, 960], [1086, 391, 1365, 786], [71, 156, 500, 485], [1079, 158, 1288, 428], [862, 1584, 1212, 2058], [961, 518, 1082, 695], [329, 251, 709, 551], [1141, 471, 1237, 623], [993, 1608, 1244, 1937], [1049, 460, 1351, 846], [1078, 1786, 1348, 2136], [1077, 1810, 1266, 2066], [1084, 1703, 1393, 2111], [657, 1223, 1411, 2112], [570, 99, 896, 623], [1085, 1572, 1414, 1987], [916, 1741, 1094, 2039], [1024, 1625, 1258, 1957], [1073, 1577, 1351, 1930], [1048, 1642, 1307, 1999], [240, 691, 625, 1001], [519, 318, 828, 759], [1035, 543, 1325, 866], [919, 1581, 1141, 1887], [1074, 1750, 1222, 1963], [699, 341, 878, 605], [1058, 1640, 1363, 2024], [1003, 1703, 1260, 2050], [1015, 1613, 1316, 2039], [1091, 1539, 1365, 1923], [933, 1445, 1316, 1934], [698, 419, 878, 703], [732, 1777, 854, 1999], [718, 1541, 1173, 2096], [964, 1615, 1214, 2058], [1064, 1742, 1234, 2025], [1064, 1610, 1266, 2050], [1070, 266, 1270, 656], [784, 138, 1334, 814], [1157, 482, 1373, 638], [823, 1875, 933, 2060], [914, 211, 1281, 668], [988, 474, 1252, 809], [958, 1642, 1288, 2071], [121, 1823, 326, 1977], [945, 304, 1089, 491], [805, 1745, 925, 1934], [1072, 1567, 1264, 1826], [1086, 1814, 1304, 2087], [822, 632, 1051, 931], [1037, 1570, 1164, 1746], [1005, 1306, 1171, 1535], [1023, 504, 1253, 787], [976, 1671, 1290, 2036], [996, 1608, 1299, 2021], [1060, 450, 1250, 708], [1043, 471, 1246, 744], [981, 1529, 1231, 1837], [521, 177, 884, 659], [1049, 613, 1241, 864], [1028, 1687, 1278, 2026], [631, 364, 871, 698], [1189, 1743, 1382, 2000], [1101, 1324, 1232, 1513], [1000, 368, 1248, 694], [879, 1575, 1075, 1854], [123, 423, 491, 788], [809, 1490, 1250, 2040], [970, 1709, 1245, 2076], [1069, 1660, 1226, 1914], [939, 1513, 1337, 2040], [1130, 496, 1371, 672], [842, 1746, 1020, 2013], [1053, 372, 1402, 828], [543, 460, 736, 748], [651, 1866, 769, 2081], [606, 220, 864, 402], [862, 1664, 1170, 2097], [1072, 643, 1221, 878], [695, 1537, 1130, 2144], [1032, 1037, 1344, 1451], [734, 218, 1041, 611], [1115, 1739, 1280, 1979], [1052, 571, 1246, 817], [976, 1705, 1121, 2016], [1011, 1533, 1332, 2009], [517, 118, 1375, 1196], [1067, 269, 1375, 510], [214, 272, 499, 683], [659, 118, 1109, 707], [920, 354, 1099, 645], [837, 297, 944, 461], [835, 1804, 978, 2037], [867, 1519, 1098, 1881], [740, 1825, 897, 2103], [207, 1833, 345, 2051], [373, 1550, 664, 2040], [391, 348, 683, 737], [566, 1646, 747, 1952], [723, 1754, 836, 1958], [668, 434, 794, 652], [759, 1629, 933, 1933], [763, 1877, 941, 2135], [774, 1610, 990, 1986], [859, 1462, 1213, 2035], [805, 1695, 1062, 2142], [764, 151, 993, 536], [782, 122, 974, 436], [183, 1742, 300, 1958], [153, 1165, 331, 1269], [219, 1629, 361, 1865], [444, 1751, 571, 1971], [747, 344, 882, 568], [284, 1692, 606, 1932], [40, 1594, 258, 1946], [307, 1035, 525, 1168], [782, 561, 928, 782], [830, 1593, 1035, 1923], [218, 1376, 447, 1724], [647, 1452, 1255, 1936], [758, 1436, 944, 1773], [162, 682, 440, 856], [1201, 486, 1421, 817], [834, 707, 1156, 936], [752, 221, 955, 554], [786, 1486, 1150, 2038], [452, 305, 626, 602], [809, 253, 921, 456], [768, 1994, 844, 2134], [1192, 973, 1396, 1089], [1102, 1005, 1282, 1104], [915, 1797, 1091, 2124], [483, 158, 798, 668], [739, 1643, 950, 2010], [87, 1612, 698, 2051], [560, 1514, 769, 1896], [33, 511, 447, 776], [243, 138, 520, 515], [413, 1647, 746, 1949], [715, 1556, 965, 1922], [405, 93, 517, 280], [948, 1691, 1087, 1943], [93, 268, 499, 538], [59, 252, 689, 741], [1124, 129, 1283, 392], [230, 90, 616, 643], [494, 613, 613, 837], [378, 1816, 523, 2102], [1085, 777, 1317, 959], [1014, 822, 1248, 962], [152, 249, 373, 615], [792, 119, 1230, 726], [710, 1763, 805, 1935], [764, 1927, 850, 2087], [1012, 1059, 1317, 1250], [782, 97, 1237, 529], [1075, 750, 1243, 843], [794, 1920, 843, 2013], [558, 119, 833, 528], [990, 1863, 1123, 2073], [793, 260, 1047, 595], [1008, 1748, 1147, 1949], [704, 164, 914, 477], [507, 247, 833, 666], [61, 394, 542, 759], [926, 1543, 1227, 1943], [859, 1722, 1105, 2054], [1004, 1935, 1135, 2132], [36, 510, 597, 1006], [695, 130, 1106, 532], [481, 1796, 595, 2048], [112, 911, 621, 1287], [1013, 377, 1337, 903], [909, 137, 1397, 878], [687, 84, 1131, 902], [862, 1535, 1163, 2018], [1029, 377, 1391, 859], [954, 360, 1340, 896], [69, 309, 417, 577], [739, 168, 912, 437], [534, 1385, 1061, 2112], [947, 533, 1386, 1082], [692, 317, 1112, 1026], [712, 1754, 929, 2141], [91, 1609, 314, 1966], [738, 503, 972, 900], [799, 466, 1074, 931], [783, 1236, 1268, 2001], [747, 1468, 1109, 2079], [773, 301, 1057, 785], [758, 334, 1047, 826], [786, 1676, 1017, 2075], [762, 1454, 1206, 2175], [736, 1637, 895, 1913], [865, 1363, 1194, 1920], [879, 772, 1134, 1185], [953, 184, 1301, 588], [697, 1833, 876, 2129], [787, 1312, 1283, 2083], [735, 108, 1100, 681], [691, 1611, 957, 2076], [685, 417, 1218, 1278], [955, 1367, 1264, 1882], [1097, 247, 1220, 434], [1110, 964, 1332, 1124], [690, 1408, 1301, 2102], [1118, 354, 1319, 620], [726, 1521, 1143, 2053], [991, 419, 1244, 620], [954, 1800, 1153, 2068], [994, 1769, 1241, 2105], [983, 271, 1278, 650], [1051, 1683, 1299, 2027], [1111, 842, 1298, 976], [1027, 204, 1333, 541], [1058, 243, 1338, 416], [1050, 242, 1377, 633], [1031, 1716, 1251, 2112], [1119, 1640, 1395, 1980], [1176, 1879, 1301, 2065], [1189, 329, 1345, 453], [1072, 1714, 1285, 2035], [1126, 347, 1384, 559], [1033, 1701, 1283, 2024], [869, 1568, 1276, 2067], [897, 1759, 1058, 2032], [734, 137, 1352, 893], [1109, 1899, 1239, 2119], [1176, 687, 1381, 831], [1130, 1790, 1280, 2008], [233, 875, 586, 1145], [972, 1486, 1257, 2091], [976, 1626, 1247, 1996], [1019, 257, 1226, 409], [483, 1643, 741, 2027], [794, 1658, 1218, 2075], [1169, 1833, 1378, 2127], [250, 1627, 621, 2086], [1033, 261, 1175, 360], [1118, 483, 1354, 669], [1099, 425, 1342, 631], [1018, 1458, 1373, 1854], [1104, 1774, 1220, 1933], [545, 355, 780, 669], [180, 86, 592, 607], [1176, 985, 1332, 1087], [1093, 752, 1279, 895], [1158, 1700, 1337, 1977], [1084, 618, 1266, 841], [1075, 1689, 1241, 1920], [1119, 644, 1364, 822], [856, 208, 1333, 603], [967, 167, 1222, 508], [1026, 128, 1299, 486], [1074, 1660, 1312, 2083], [1213, 819, 1387, 1061], [1027, 1392, 1169, 1597], [1079, 1597, 1256, 1862], [423, 1643, 677, 1996], [1005, 1735, 1164, 1964], [952, 1692, 1243, 2070], [679, 190, 940, 535], [675, 211, 954, 423], [183, 1397, 685, 2093], [941, 1735, 1156, 2121], [1041, 1819, 1218, 2079], [1081, 273, 1353, 492], [657, 140, 991, 432], [815, 1472, 1391, 2113], [866, 227, 1349, 634], [1091, 413, 1351, 616], [1075, 1734, 1319, 2064], [1062, 1658, 1324, 2014], [480, 175, 989, 786], [565, 1765, 732, 2038], [815, 1557, 1124, 1957], [1052, 1710, 1191, 1927], [564, 1757, 673, 1931], [1070, 1818, 1240, 2068], [1126, 1767, 1353, 2123], [1111, 1785, 1261, 2019], [442, 1596, 800, 2080], [1055, 1772, 1260, 2046], [882, 1798, 1067, 2079], [1102, 1746, 1289, 2023], [1128, 1874, 1308, 2126], [1074, 219, 1379, 418], [643, 291, 956, 535], [1001, 534, 1298, 923], [337, 301, 610, 685], [1034, 1662, 1326, 2048], [1044, 926, 1393, 1214], [784, 1636, 1218, 2143], [869, 1528, 1320, 2016], [1103, 1563, 1237, 1770], [1123, 1650, 1264, 1849], [1050, 1627, 1194, 1833], [1018, 1711, 1323, 2072], [283, 199, 600, 444], [1097, 1594, 1280, 1846], [238, 1349, 595, 1869], [730, 125, 1384, 952], [918, 1412, 1255, 1883], [864, 511, 1311, 886], [933, 169, 1312, 475], [817, 1088, 1397, 1314], [958, 1583, 1324, 2063], [924, 1386, 1233, 1591], [839, 314, 1059, 499], [953, 434, 1124, 584], [918, 620, 1147, 1064], [629, 1344, 897, 1696], [549, 728, 900, 922], [422, 1479, 821, 2102], [507, 507, 853, 723], [743, 433, 1151, 1044], [651, 1782, 787, 1969], [513, 90, 1093, 888], [276, 1352, 627, 1853], [468, 520, 878, 1103], [837, 280, 1336, 977], [662, 1250, 841, 1509], [336, 1509, 654, 2050], [670, 139, 1222, 943], [670, 362, 1084, 994], [508, 1378, 971, 2120], [719, 1349, 1127, 1995], [358, 243, 742, 805], [733, 1656, 995, 2075], [654, 1246, 863, 1577], [577, 851, 835, 1231], [864, 292, 1269, 858], [766, 360, 1122, 951], [714, 427, 1082, 999], [656, 1186, 945, 1653], [706, 1610, 952, 2020], [698, 493, 1044, 1041], [176, 256, 517, 800], [665, 1163, 1014, 1717], [181, 1322, 386, 1643], [840, 1470, 1275, 2127], [783, 200, 1232, 882], [875, 358, 1215, 860], [743, 556, 1053, 1031], [827, 399, 1286, 1066], [773, 419, 1112, 876], [685, 1315, 1144, 2031], [753, 385, 1164, 996]]

# load groundtruth
groundtruth = loadmat('./datasets/groundtruth&coordinates/ColorCheckerData.mat')

# load the training pictures list
train_picture_list = glob.glob(os.path.join(train_picture_path, "*"))
# sorted by name
def get_order(elem):
    return eval(os.path.splitext(os.path.basename(elem))[0].split('_')[0])
train_picture_list.sort(key=get_order)

# network structure
def batch_norm(inp,name="batch_norm"):
    batch_norm_fi = tf.keras.layers.BatchNormalization()(inp, training=True)
    return batch_norm_fi
def lrelu(x, leak=0.2, name = "lrelu"):
    return tf.maximum(x, leak*x)
gen_input = tf.keras.Input(shape=(480,480,3), name='train_img')
c1 = tf.keras.layers.Conv2D(filters=96,kernel_size=3,strides=2,padding='same',input_shape=[None,None,3])(gen_input)
b1 = batch_norm(c1)
c2 = tf.keras.layers.Conv2D(filters=256,kernel_size=3,strides=2,padding='same',use_bias=False)(lrelu(b1))
b2 = batch_norm(c2)
c3 = tf.keras.layers.Conv2D(filters=384,kernel_size=3,strides=2,padding='same',use_bias=False)(lrelu(b2))
b3 = batch_norm(c3)
d1 = tf.keras.layers.Conv2DTranspose(256,kernel_size=3,strides=2,padding='same',use_bias=False)(tf.nn.relu(b3))
d1 = tf.concat([batch_norm(d1, name='g_bn_d1'), b2],3)
d2 = tf.keras.layers.Conv2DTranspose(96,kernel_size=3,strides=2,padding='same',use_bias=False)(tf.nn.relu(d1))
d2 = tf.concat([batch_norm(d2, name='g_bn_d1'), b1],3)
d3 = tf.keras.layers.Conv2DTranspose(4,kernel_size=3,strides=2,padding='same',use_bias=False)(tf.nn.relu(d2))
gen_out = tf.nn.tanh(d3)
gen_model = tf.keras.Model(inputs=gen_input, outputs=gen_out, name='gen_model')
generator_optimizer = tf.keras.optimizers.Adam(lr=learning_rate)

# calculate l1 loss
def l1_loss(src, dst):
    return tf.reduce_mean(tf.abs(src - dst))

# each training step
def train_step(batch_picture,batch_label,ill_gt,counter):
    with tf.GradientTape() as gen_tape:  # get gradients
        gen_label = gen_model(batch_picture)  # get generated label
        gen_label_wb =  (gen_label[0,:,:,1:4] + 1.0)/2.0  # the generated label (corrected by the network)
        ori_picture = (batch_picture + 1.0)/2.0  # the original input
        label_picture = (batch_label + 1.0)/2.0  # the groundtruth label
        L1_loss = tf.reduce_mean(l1_loss(gen_label_wb, label_picture))  # l1 loss
        # the weight-map
        weight = (gen_label[0,:,:,0] + 1.0)/2.0
        weight = tf.clip_by_value(weight, 0, 1.0)
        weight = tf.expand_dims(weight,0)
        weight = tf.expand_dims(weight,-1)
        # calculate illuminant loss
        gen_illum = np.mean(weight*ori_picture,axis=(1,2))/tf.reduce_mean(weight*gen_label_wb,axis=(1,2))
        gen_illum /= tf.reduce_sum(gen_illum)  # estimated illuminant
        ill_loss_up = tf.reduce_sum(gen_illum*ill_gt)
        ill_loss_down = math.sqrt((ill_gt*ill_gt).sum())*tf.sqrt(tf.reduce_sum(gen_illum*gen_illum))
        ill_loss = ill_loss_up/ill_loss_down  # the smaller the illuminant loss, the better
        safe_v = 0.999999
        ill_loss = tf.clip_by_value(ill_loss,-safe_v,safe_v)
        # total loss
        gen_loss = L1_loss + tf.acos(ill_loss)

    # calculate gradients
    gradients_of_generator = gen_tape.gradient(gen_loss, gen_model.trainable_variables)
    # gradient descent
    generator_optimizer.apply_gradients(zip(gradients_of_generator, gen_model.trainable_variables))
    return gen_loss,gen_label_wb,ill_loss,weight

# get the file path of the mask picture
def get_mask_name(picture_name):
    if picture_name.split('_')[1] == 'IMG':
        mask_name = 'mask1_' + picture_name.split('_')[1] + '_' + picture_name.split('_')[2] + '.tiff'  #mask名称
    else:
        mask_name = 'mask1_' + picture_name.split('_')[1] + '.tiff'
    mask_path = './datasets/masks/' + mask_name
    return mask_path

# training log
f=open(model_name + '_' + train_fold + '_records.txt',"w+")

# preprocessing in each traing step
def preprocess(step):
	flag = train_set[step] - 1
	x,y,m,n = coordinates[flag]  # get coordinates
	img_path = train_picture_list[flag]  # the file path of the current training picture
	picture_name, _ = os.path.splitext(os.path.basename(img_path))  # picture name
	picture =  cv2.imread(img_path)  # read picture
	illum = groundtruth['REC_groundtruth'][flag]  # load the illuminant groundtruth of the current training picture
	illum /= illum.sum()  # normalized

	# avoid colorchecker area and randomly crop out 480*480 image patches
	height = picture.shape[0]
	width = picture.shape[1]
	colorchecker_x = [i for i in range(x,m+1)]
	colorchecker_y = [i for i in range(y,n+1)]
	while True:
	    x1 = random.randint(0, height-480)
	    crop_x = [i for i in range(x1, x1+480)]
	    y1 = random.randint(0, width-480)
	    crop_y = [i for i in range(y1, y1+480)]
	    if set(crop_x)&set(colorchecker_x)==set() or set(crop_y)&set(colorchecker_y)==set():
	        break
	cropPic = picture[(x1):(x1 + 480), (y1):(y1 + 480)]

	picture = cv2.cvtColor(cropPic, cv2.COLOR_BGR2RGB).astype(np.float64)  # BGR -> RGB
	picture = picture/255.0  # normalized (adjust the pixel value to 0~1)
	picture_wb = np.clip(picture/illum, 0, 1)  # get the corresponding groundtruth
	input_img = np.clip(picture*2 - 1, -1, 1)  # standardization
	input_label = np.clip(picture_wb*2 - 1, -1, 1) 

    # batched
	batch_picture = np.expand_dims(np.array(input_img).astype(np.float32), axis = 0)
	batch_label = np.expand_dims(np.array(input_label).astype(np.float32), axis = 0)

	# randomly flip and rotate
	if np.random.randint(2, size=1)[0] == 1:  # random flip
	    batch_picture = np.flip(batch_picture, axis=1)
	    batch_label = np.flip(batch_label, axis=1)
	if np.random.randint(2, size=1)[0] == 1:
	    batch_picture = np.flip(batch_picture, axis=2)
	    batch_label = np.flip(batch_label, axis=2)
	if np.random.randint(2, size=1)[0] == 1:  # random transpose
	    batch_picture = np.transpose(batch_picture, (0, 2, 1, 3))
	    batch_label = np.transpose(batch_label, (0, 2, 1, 3))

	return batch_picture, batch_label, illum, picture_name

# save image results
def save_image(gen_label, batch_picture, batch_label, weight, save_path, epoch, counter, picture_name):
    out_img = (gen_label) * 255
    out_img = np.clip(out_img.numpy(),0,255).astype(np.uint8)
    #out_img = cv2.resize(out_img, (height, width))
    ori_img = np.clip(((batch_picture[0] + 1.0)/2.0 * 255),0,255).astype(np.uint8)
    lab_img = np.clip(((batch_label[0] + 1.0)/2.0 * 255),0,255).astype(np.uint8)
    weight_img = cv2.cvtColor((weight[0] * 255).numpy(),cv2.COLOR_GRAY2RGB)
    weight_img = np.clip(weight_img,0,255).astype(np.uint8)
    weight_out = np.clip((255*weight[0]*gen_label).numpy(),0,255).astype(np.uint8)
    save_img = np.concatenate((ori_img,out_img,weight_img,weight_out,lab_img), axis=1)
    write_image_name = save_path + str(epoch) + '_' + str(counter) + '_' + picture_name + ".png"
    cv2.imwrite(write_image_name, save_img[:, :, (2, 1, 0)])

# start training
def train():
    counter = 0
    # determine the training fold
    if train_fold == 'fold1':
        train_set = tr_fold1
        test_set = te_fold1
    elif train_fold == 'fold2':
        train_set = tr_fold2
        test_set = te_fold2
    elif train_fold == 'fold3':
        train_set = tr_fold3
        test_set = te_fold3
    else:
        print('input fold error!')
        sys.exit()
    for epoch in range(epochs):
        # randomly shuffle the order
        random.shuffle(train_set)
        random.shuffle(test_set)
        # manually set the learning_rate decay
        global learning_rate
        if epoch == 1000:
            learning_rate = 1e-5
        if epoch == 3000:
            learning_rate = 1e-6
        train_errors = []
        # each picture in each training step
        for step in range(len(train_set)):
        	counter += 1
        	batch_picture, batch_label, illum, picture_name = preprocess(step) # get the traing batch
            gen_loss,gen_label,dis_loss,ill_loss,weight = train_step(batch_picture,batch_label,illum,counter)  # feed into the network for training
            
            # record the angle error
            ang = 180*math.acos(ill_loss.numpy())/math.pi
            train_errors.append(ang)

            # save the training image results per 1000 steps
            if counter % 1000 == 0:
            	save_image(gen_label, batch_picture, batch_label, weight, train_save_path, epoch, counter, picture_name)
            
            # save the training information in the log
            if step % 100 == 0:
                print('epoch {:d} step {:d} \t gen_loss = {:.3f}, dis_loss = {:.3f}, ill_loss = {:.3f}, ang = {:.3f}'.format(epoch, step, gen_loss, dis_loss, ill_loss, ang),file=f,flush=True)
            print('epoch {:d} step {:d} \t gen_loss = {:.3f}, dis_loss = {:.3f}, ill_loss = {:.3f}, ang = {:.3f}'.format(epoch, step, gen_loss, dis_loss, ill_loss, ang),file=sys.stdout)
        print('train mean = {:.3f}, med = {:.3f}, tri={:.3f}, best25 = {:.3f}, worst25 = {:.3f}, q95 = {:.3f}, max = {:.3f}'.format(np.mean(train_errors), np.median(train_errors), (np.percentile(train_errors,25) + 2*np.percentile(train_errors,50) + np.percentile(train_errors,75))/4, np.mean(np.sort(train_errors)[0:int(0.25*len(train_errors))]), np.mean(np.sort(train_errors)[len(train_errors)-int(0.25*len(train_errors)):len(train_errors)]), np.percentile(train_errors,95), np.max(train_errors)),file=f,flush=True)
        print('train mean = {:.3f}, med = {:.3f}, tri={:.3f}, best25 = {:.3f}, worst25 = {:.3f}, q95 = {:.3f}, max = {:.3f}'.format(np.mean(train_errors), np.median(train_errors), (np.percentile(train_errors,25) + 2*np.percentile(train_errors,50) + np.percentile(train_errors,75))/4, np.mean(np.sort(train_errors)[0:int(0.25*len(train_errors))]), np.mean(np.sort(train_errors)[len(train_errors)-int(0.25*len(train_errors)):len(train_errors)]), np.percentile(train_errors,95), np.max(train_errors)),file=sys.stdout)

        # testing after each epoch of training
        print('start evaluating...')
        evaluate(test_set,epoch)

# start evaluating
def evaluate(fold,epoch):
    test_set = fold
    test_errors = []
    for step in range(len(test_set)):
        flag = test_set[step] - 1
        img_path = train_picture_list[flag]
        picture_name, _ = os.path.splitext(os.path.basename(img_path))
        mask = cv2.imread(get_mask_name(picture_name))
        picture =  cv2.imread(img_path)
        picture[mask == 0] = 1e-5
        illum = groundtruth['REC_groundtruth'][flag]
        illum /= illum.sum()
        picture = cv2.resize(picture, (480,480))
        picture = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB).astype(np.float64)
        picture = picture/255.0
        picture_wb = np.clip(picture/illum, 0, 1)
        input_img = np.clip(picture*2 - 1, -1, 1)
        input_label = np.clip(picture_wb*2 - 1, -1, 1)
        batch_picture = np.expand_dims(np.array(input_img).astype(np.float32), axis = 0)
        gen_label = gen_model(batch_picture)
        gen_label_wb =  (gen_label[0,:,:,1:4] + 1.0)/2.0
        ori_picture = (batch_picture + 1.0)/2.0
        weight = (gen_label[0,:,:,0] + 1.0)/2.0
        weight = tf.expand_dims(weight,0)
        weight = tf.expand_dims(weight,-1)
        gen_illum = np.mean(weight*ori_picture,axis=(1,2))/tf.reduce_mean(weight*gen_label_wb,axis=(1,2))
        gen_illum /= tf.reduce_sum(gen_illum)
        ill_loss_up = tf.reduce_sum(gen_illum*illum)
        ill_loss_down = math.sqrt((illum*illum).sum())*tf.sqrt(tf.reduce_sum(gen_illum*gen_illum))
        ill_loss = ill_loss_up/ill_loss_down
        safe_v = 0.999999
        ill_loss = tf.clip_by_value(ill_loss,-safe_v,safe_v)
        ang = 180*math.acos(ill_loss)/math.pi
        test_errors.append(ang)

        # save the testing image results every 10 rounds and 100 steps
        if epoch%10 == 0 and step%100 == 0:
        	save_image(gen_label_wb, input_img, input_label, weight, test_save_path, epoch, step, picture_name)

    print('test mean = {:.3f}, med = {:.3f}, tri={:.3f}, best25 = {:.3f}, worst25 = {:.3f}, q95 = {:.3f}, max = {:.3f}'.format(np.mean(test_errors), np.median(test_errors), (np.percentile(test_errors,25) + 2*np.percentile(test_errors,50) + np.percentile(test_errors,75))/4, np.mean(np.sort(test_errors)[0:int(0.25*len(test_errors))]), np.mean(np.sort(test_errors)[len(test_errors)-int(0.25*len(test_errors)):len(test_errors)]), np.percentile(test_errors,95), np.max(test_errors)),file=f,flush=True)
    print('test mean = {:.3f}, med = {:.3f}, tri={:.3f}, best25 = {:.3f}, worst25 = {:.3f}, q95 = {:.3f}, max = {:.3f}'.format(np.mean(test_errors), np.median(test_errors), (np.percentile(test_errors,25) + 2*np.percentile(test_errors,50) + np.percentile(test_errors,75))/4, np.mean(np.sort(test_errors)[0:int(0.25*len(test_errors))]), np.mean(np.sort(test_errors)[len(test_errors)-int(0.25*len(test_errors)):len(test_errors)]), np.percentile(test_errors,95), np.max(test_errors)),file=sys.stdout)
    
    # record the best results and then save the model
    global best_record
    if np.mean(test_errors) < best_record:
        gen_model.save_weights(model_save_path)
        best_record = np.mean(test_errors)

if __name__ == '__main__':
    train()