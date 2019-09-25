using System;
using System.Collections.Generic;
using System.Linq;

namespace SoundPlayground.Core {
    public static class IEnumerableExtensions {
        public static IEnumerable<T> MergeSorted <T, O> ( Func<T, O> order, params IEnumerable<T>[] enumerables ) where O : IComparable<O> {
            return enumerables.MergeSorted( order );
        }

        public static IEnumerable<T> MergeSorted <T> ( this IEnumerable<IEnumerable<T>> enumerables ) where T : IComparable<T> {
            return MergeSorted( enumerables, x => x );
        }

        /// <summary>
        /// This method works on any enumerable of enumerables. Each of the children enumerables are expected to yield their elements
        /// in order. This method returns a single enumerable containing all elelments in the right order
        /// </summary>
        /// <param name="enumerables"></param>
        /// <param name="order"></param>
        /// <typeparam name="T"></typeparam>
        /// <typeparam name="O"></typeparam>
        /// <returns></returns>
        public static IEnumerable<T> MergeSorted <T, O> ( this IEnumerable<IEnumerable<T>> enumerables, Func<T, O> order ) where O : IComparable<O> {
            var items = enumerables.Select( en => en.GetEnumerator() )
                .Where( en => en.MoveNext() )
                .Select( enumerator => ( order( enumerator.Current ), enumerator ) )
                .OrderBy( en => en.Item1 )
                .ToList();

            try {
                while ( items.Count > 0 ) {
                    var next = items[ 0 ];

                    yield return next.enumerator.Current;

                    items.RemoveAt( 0 );

                    if ( next.enumerator.MoveNext() ) {
                        var value = order( next.enumerator.Current );

                        var i = 0;

                        for (; i <= items.Count; i++) {
                            if ( i == items.Count || value.CompareTo( items[ i ].Item1 ) <= 0 ) {
                                items.Insert( i, ( value, next.enumerator ) );

                                break;
                            }
                        }
                    } else next.enumerator.Dispose();
                }
            } finally {
                items.ForEach( en => en.enumerator.Dispose() );

                items = null;
            }            
        }
    } 
}
