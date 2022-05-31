import warnings

DFLT_N_FREQ = 1025
DFLT_FREQ_RANGE = (0, DFLT_N_FREQ)


def make_buckets(n_buckets=15, freqs_weighting=lambda x: x,
                 freq_range=DFLT_FREQ_RANGE, non_empty_bucket=True,
                 reverse=False):
    """
    Create greedily buckets starting by aggregating lower frequencies, when the sum of
    the frequencies values so far exceed the number of buckets created times the target
    average value for a single bucket, a new bucket is created with or without the last
    term according to which choice will be closest to the target

    :param n_buckets: final number of buckets
    :param freqs_weighting: any function assigning a non-negative value to each
                            element in the freq_range
                            If given a list, the function will be assumed
                            to be the one to one mapping the frequencies to the value in the list

    :param freq_range: the range of frequencies considered, inclusive on both ends
    :param non_empty_bucket: if set to true, all buckets will have at least one element
    :param reverse: if set to true, will start aggregating higher frequencies instead, which for an increasing weight
    function will aggregate the higher frequencies into larger bins as typical
    :return: a partition of freq_range

    >>> buckets = make_buckets(n_buckets=15, freqs_weighting=lambda x: np.log(x + 0.001), freq_range=(200, 1000))
    >>> len(buckets) == 15
    True
    >>> buckets[0][0] # the first bucket starts at the first term of freq_range
    200
    >>> buckets[-1][-1] # the last bucket ends at the last term of freq_range - 1
    999

    """

    # total number of frequencies
    low_freq = freq_range[0]
    high_freq = freq_range[1]
    n_freqs = high_freq - low_freq
    if n_freqs < n_buckets and non_empty_bucket:
        warnings.warn('You asked for more buckets than the number of frequencies available, '
                      'some will necessarily be empty')
        non_empty_bucket = False

    # indices of the frequencies
    freq_range = list(range(low_freq, high_freq + 1))
    if reverse:
        freq_range.reverse()
    # get the value of each frequency
    if not hasattr(freqs_weighting, '__iter__'):
        freq_values = list(map(freqs_weighting, freq_range))
    else:
        freq_values = freqs_weighting
    # ideal average sum of bucket value
    target_bucket_sum = sum(freq_values) / n_buckets

    # position of the next term to consider
    position = 0
    # sum of all the existing buckets plus the current bucket under construction
    existing_bucket_sum = 0
    # list of indices for each bucket, empty at moment
    idx_bucket_list = []

    for idx in range(n_buckets):
        # the list of indices in the bucket under construction
        bucket_idx = []
        while existing_bucket_sum < target_bucket_sum * (idx + 1):
            bucket_idx.append(position)
            existing_bucket_sum += freq_values[position]
            # increment the position if we are not running out of terms
            if position < n_freqs - 1:
                position += 1
            # otherwise we stop and return all the buckets, including the one under construction
            # which is non empty by construction
            else:
                idx_bucket_list.append(bucket_idx)
                if low_freq > 0:
                    idx_bucket_list = [[i + low_freq for i in l] for l in idx_bucket_list]
                return idx_bucket_list

        # if we skipped the loop above, our newly constructed bucket is empty
        # if we specified that empty buckets are not ok, we force one guy in it
        if non_empty_bucket and len(bucket_idx) == 0:
            bucket_idx.append(position)
            idx_bucket_list.append(bucket_idx)
            # increment the position if we are not running out of terms
            if position < n_freqs - 1:
                position += 1
            # otherwise we stop and return all the buckets, including the one under construction
            # which is non empty by construction
            else:
                return idx_bucket_list

        else:
            # we now have a non empty bucket, so we check what is best, including the last added term or no
            total_dif_small = abs(existing_bucket_sum - freq_values[position] - target_bucket_sum * (idx + 1))
            total_diff_large = abs(existing_bucket_sum - target_bucket_sum * (idx + 1))

            # we don't remove the last if it is better not too or if we want non empty buckets
            # and remove it would violate that rule
            if total_diff_large < total_dif_small or (len(bucket_idx) < 2 and non_empty_bucket):
                idx_bucket_list.append(bucket_idx)
            # otherwise remove last term
            else:
                idx_bucket_list.append(bucket_idx[:-1])
                # below is to ensure that if the last bucket is empty, we increment the position
                # effectively skipping that position. Otherwise we will end up with a list of empty lists
                if len(bucket_idx[:-1]) > 0:
                    existing_bucket_sum -= freq_values[position]
                    position -= 1
                else:
                    pass

    idx_bucket_list[-1] = freq_range[idx_bucket_list[-1][0]:]
    if low_freq > 0:
        idx_bucket_list = [[i + low_freq for i in l] for l in idx_bucket_list]

    return idx_bucket_list


def make_buckets_simple(n_bucket=10, row_weights_func=lambda x: 1 + x, n_freq=20):
    """
    :param n_bucket: int, the number of buckets to create
    :param row_weights_func: a function, non zero on the integers values from 0 to n_freq. The relative values from
                             one integer a to a + 1 will become the relative number of non zero values from row a to
                             row a + 1. Note that everything has to be rounded so the actual relationship is a bit more
                             complex. The rounding follows two rules:
                             1) at least 1 in row
                             2) the excess or lack are removed from the end, one unit per index
    :param n_freq: int, the total number of frequencies, i.e, indices in buckets
    :return: a list of list of indices, consecutive, starting at 0 and ending at n_freq

    >>> make_buckets_simple(row_weights_func=lambda x: 1+x)
    [[0], [1], [2], [3], [4, 5], [6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16], [17, 18, 19, 20]]
    """

    row_weights = [row_weights_func(i) for i in range(n_bucket)]
    total_weights = np.sum(row_weights)
    n_non_zero_entry_per_unit = n_freq / total_weights
    ideal_n_per_row = [n_non_zero_entry_per_unit * w for w in row_weights]
    actual_per_row = []
    remainder = 0
    for count in ideal_n_per_row:
        rounded_count = int(max(1, round(count)))
        remainder += count - rounded_count
        actual_per_row.append(rounded_count)
    n_to_correct = int(np.abs(remainder))
    for i in range(1, n_to_correct + 1):
        actual_per_row[-i] = int(actual_per_row[-i] + np.sign(remainder))
    buckets = []
    idx = 0
    for n_in_row in actual_per_row:
        buckets.append(list(range(idx, idx + n_in_row)))
        idx += n_in_row
    return buckets


def hertz_to_mel(hertz):
    """convert a frequency given in hertz into mel"""

    return 2595 * np.log10(1 + hertz / 700)


def mel_to_hertz(mel):
    """convert a frequency given in mel into hertz"""

    return (10 ** (mel / 2595) - 1) * 700


def buckets_conversion(buckets, conversion_function=hertz_to_mel):
    """
    Convert buckets in one scale to another through the conversion_function.
    For example, if the conversion_function is set to hertz_to_mel, the function fed with hertz buckets
    will return the equivalent mel buckets.
    :param buckets: list of list of frequencies in one scale
    :param conversion_function: a mapping from frequencies in one scale to another
    :return: the converted buckets
    """

    separators = [-1]
    for bucket in buckets:
        separators.append(max(bucket))
    new_separators = [int(round(conversion_function(sep))) for sep in separators]
    new_buckets = [range(new_separators[i] + 1, new_separators[i + 1] + 1) for i in range(len(new_separators) - 1) if
                   range(new_separators[i], new_separators[i + 1]) != []]
    return new_buckets


def visualize_buckets(buckets, cmap='Spectral'):
    """
    Makes a plot of the buckets using a heatmap
    :param buckets: a list of the list of indices for each bucket
    :return: a plot
    """

    import matplotlib.pyplot as plt
    colors = []
    all_indices = [item for sublist in buckets for item in sublist]
    buckets.reverse()
    min_idx = min(all_indices)
    max_idx = max(all_indices)
    aspect = 10 / (max_idx - min_idx)
    for i, bucket in enumerate(buckets):
        for repeat in range(len(bucket)):
            colors.append([1 / (i + 1)])
    plt.imshow(colors, cmap=cmap, interpolation='nearest', aspect=aspect)
    plt.axis('off')
    plt.title('high frequencies on top')
    plt.show()


def make_band_matrix_row(list_entries, row_len):
    """
    Makes a row for the spectral bucket matrix. The row is zero everywhere except on the entries of index in
    list_entries where it is 1 / len(list_entries)

    :param list_entries: the indices of non zero entries of the row
    :param row_len: the length of the row
    :return: an array of length row_len as described above

    >>> make_band_matrix_row([3], 5)
    array([0., 0., 0., 1., 0.])
    >>> make_band_matrix_row([0, 3], 5)
    array([0.5, 0. , 0. , 0.5, 0. ])

    """

    n_non_zero = len(list_entries)
    row = np.array([0 if i not in list_entries else 1 / n_non_zero for i in range(row_len)])
    return row


def make_band_matrix(buckets, n_freq=DFLT_N_FREQ):
    """
    Given a list of n list of indices, make a matrix of size n by n_freq where the entries of row k are 0
    everywhere except at the index in the k list of buckets, where the entries are the inverse of the length
    of that bucket

    :param buckets: a list of list containing the indices of non zero entries of the corresponding row
    :param n_freq: the number of column of the matrix
    :return: a len(buckets) by n_freq matrix

    >>> buckets = make_buckets(n_buckets=15, freqs_weighting=lambda x: np.log(x + 0.001), freq_range=(200, 1000))
    >>> M = make_band_matrix(buckets, n_freq=1025)
    >>> print(M.shape)
    (15, 1025)

    >>> # the matrix sends each of the 200 first unitary vector to the zero vector (not below is not a mathematical proof of that, but solid clue)
    >>> vec = [1] * 200 + [0] * (1025 - 200)
    >>> print(np.dot(M, vec))
    [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]

    >>> # after that, we get non zero output (in general at least)
    >>> vec = [1] * 200 + [1] + [0] * (1025 - 201)
    >>> print(np.dot(M, vec))
    [0.01612903 0.         0.         0.         0.         0.
     0.         0.         0.         0.         0.         0.
     0.         0.         0.        ]

    """

    n_bands = len(buckets)
    bucket_matrix = np.zeros((n_bands, n_freq))
    for row_idx, bucket in enumerate(buckets):
        row = make_band_matrix_row(list_entries=bucket, row_len=n_freq)
        bucket_matrix[row_idx] = row
    return bucket_matrix


def make_band_proj_matrix(n_buckets=15,
                          n_freq=DFLT_N_FREQ,
                          freqs_weighting=lambda x: x,
                          non_empty_bucket=True,
                          reverse=False):
    """
    Uses make_buckets and make_band_matrix to make a band-based projection matrix

    :param n_buckets: final number of buckets
    :param freqs_weighting: any function assigning a non-negative value to each
                            element in the freq_range
                            If given a list, the function will be assumed
                            to be the one to one mapping the frequencies to the value in the list

    :param n_freq: the number of column of the matrix
    :param non_empty_bucket: if set to true, all buckets will have at least one element
    :param reverse: if set to true, will start aggregating higher frequencies instead
    :return: a len(buckets) by n_freq matrix

    >>> make_band_proj_matrix(n_buckets=3, n_freq=10)
    array([[0.14285714, 0.14285714, 0.14285714, 0.14285714, 0.14285714,
            0.14285714, 0.14285714, 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.        , 0.        ,
            0.        , 0.        , 0.33333333, 0.33333333, 0.33333333]])

    """
    buckets = make_buckets(n_buckets, freqs_weighting, (0, n_freq), non_empty_bucket, reverse)
    return make_band_matrix(buckets, n_freq)

